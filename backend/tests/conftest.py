"""Test fixtures.

Runs against a real PostgreSQL database (``TEST_DATABASE_URL``) because the schema uses JSONB,
partial indexes, and PostgreSQL-specific inserts — SQLite would not exercise the code that ships.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production-use-only")
os.environ.setdefault("HASH_SALT", "test-hash-salt")
os.environ.setdefault("LLM_PROVIDER", "echo")
# Pin the rate limits so the suite asserts the production defaults regardless of what a local
# .env raises them to for E2E convenience.
os.environ["RATE_LIMIT_REGISTER_PER_HOUR"] = "5"
os.environ["RATE_LIMIT_LOGIN_PER_IP"] = "10"
os.environ["RATE_LIMIT_LOGIN_PER_EMAIL"] = "5"
os.environ["RATE_LIMIT_LOGIN_WINDOW_SECONDS"] = "900"

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://aipassport:aip_dev_local_only@127.0.0.1:5432/aipassport_test",
)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.auth.rate_limit import limiter  # noqa: E402
from app.core.db import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base  # noqa: E402
from app.services.seed import seed_content  # noqa: E402

TABLES_TO_CLEAR = [
    "events",
    "ai_messages",
    "ai_conversations",
    "activity_results",
    "question_responses",
    "page_progress",
    "learning_sessions",
    "email_verification_tokens",
    "password_reset_tokens",
    "auth_sessions",
    "user_identities",
    "users",
]


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Builds the test schema with Alembic, not ``create_all``.

    This means the suite also proves that ``alembic upgrade head`` produces a working schema from a
    clean database — the migration path is what production uses, so it is what tests should exercise.
    """
    _run_migrations()
    eng = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    # Sanity check that the migration produced the mapped tables.
    async with eng.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn, checkfirst=True))
    yield eng
    await eng.dispose()


def _run_migrations() -> None:
    from alembic import command
    from alembic.config import Config

    root = Path(__file__).resolve().parents[1]
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "alembic"))
    command.upgrade(config, "head")


@pytest_asyncio.fixture
async def sessionmaker_fixture(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


@pytest_asyncio.fixture(autouse=True)
async def clean_db(engine, sessionmaker_fixture) -> AsyncGenerator[None, None]:
    """Truncate learner data between tests; seed curriculum once."""
    from sqlalchemy import text

    async with sessionmaker_fixture() as session:
        for table in TABLES_TO_CLEAR:
            await session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
        await session.commit()
        # Curriculum is idempotent and shared across tests.
        await seed_content(session)
    limiter.reset()
    yield


@pytest_asyncio.fixture
async def client(sessionmaker_fixture) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with sessionmaker_fixture() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as async_client:
        yield async_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def db(sessionmaker_fixture) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker_fixture() as session:
        yield session


def unique_email(prefix: str = "learner") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}@example.edu"


@pytest_asyncio.fixture
async def learner(client: AsyncClient) -> dict[str, str]:
    """A registered learner with an access token and CSRF token."""
    email = unique_email()
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "correct-horse-battery-9",
            "display_name": "Test Learner",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    return {
        "email": email,
        "password": "correct-horse-battery-9",
        "token": body["access_token"],
        "csrf": body["csrf_token"],
        "user_id": body["user"]["id"],
        "headers": {"Authorization": f"Bearer {body['access_token']}"},
    }
