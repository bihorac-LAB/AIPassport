"""Application settings.

Every deployment-specific value is an environment variable. Development defaults are safe but
deliberately not production-viable: ``ENVIRONMENT=production`` refuses to boot on a default secret
or a wildcard CORS origin.
"""

from __future__ import annotations

import secrets
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "test", "staging", "production"]

DEV_SECRET_SENTINEL = "dev-only-insecure-secret-change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── Core ────────────────────────────────────────────────────────────────
    ENVIRONMENT: Environment = "development"
    PROJECT_NAME: str = "AIPassport API"
    API_V1_PREFIX: str = "/api/v1"
    ENABLE_DOCS: bool | None = None

    SECRET_KEY: str = DEV_SECRET_SENTINEL
    # Separate salt for hashing low-sensitivity identifiers (IP addresses) so rotating the JWT
    # secret does not invalidate stored hashes.
    HASH_SALT: str = DEV_SECRET_SENTINEL

    # ── Database ────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://aipassport:aipassport@localhost:5432/aipassport"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    # ── Frontend / CORS ─────────────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # ── Tokens ──────────────────────────────────────────────────────────────
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    PASSWORD_RESET_EXPIRE_MINUTES: int = 60
    EMAIL_VERIFY_EXPIRE_HOURS: int = 48
    REFRESH_COOKIE_NAME: str = "aip_refresh"
    CSRF_COOKIE_NAME: str = "aip_csrf"
    COOKIE_DOMAIN: str | None = None
    # None is required for Netlify -> EC2 and for Canvas iframes; paired with Secure + CORS
    # allowlist + double-submit CSRF. Use "lax" for same-site local development over http.
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    COOKIE_SECURE: bool = False

    # ── Password policy ─────────────────────────────────────────────────────
    PASSWORD_MIN_LENGTH: int = 10
    PASSWORD_MAX_LENGTH: int = 128

    # ── Learning session ────────────────────────────────────────────────────
    LEARNING_SESSION_IDLE_MINUTES: int = 30
    MAX_TIME_DELTA_SECONDS: int = 120

    # ── LLM ─────────────────────────────────────────────────────────────────
    # "auto" picks openai_compatible when a base url + key exist, else gemini when a Gemini key
    # exists, else the deterministic echo stub.
    LLM_PROVIDER: Literal["auto", "openai_compatible", "gemini", "echo"] = "auto"
    LLM_MODEL: str = "gemma-3-27b-it"
    LLM_BASE_URL: str = "https://api.ai.it.ufl.edu/v1"
    LLM_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    LLM_TIMEOUT_SECONDS: float = 30.0
    LLM_MAX_OUTPUT_TOKENS: int = 1200
    LLM_TEMPERATURE: float = 0.5

    AI_RATE_LIMIT_PER_HOUR: int = 20
    AI_RATE_LIMIT_PER_DAY: int = 200

    # ── Auth rate limits ────────────────────────────────────────────────────
    # Deliberately tight by default. Raise only for automated test environments.
    RATE_LIMIT_REGISTER_PER_HOUR: int = 5
    RATE_LIMIT_LOGIN_PER_IP: int = 10
    RATE_LIMIT_LOGIN_PER_EMAIL: int = 5
    RATE_LIMIT_LOGIN_WINDOW_SECONDS: int = 900

    # ── SMTP (optional in development) ──────────────────────────────────────
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "aipassport@example.edu"
    SMTP_STARTTLS: bool = True

    # ── Logging ─────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool | None = None

    # ── Derived ─────────────────────────────────────────────────────────────
    @field_validator("CORS_ORIGINS")
    @classmethod
    def _strip_origins(cls, v: str) -> str:
        return ",".join(part.strip().rstrip("/") for part in v.split(",") if part.strip())

    @property
    def cors_origin_list(self) -> list[str]:
        return [o for o in self.CORS_ORIGINS.split(",") if o]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT in ("production", "staging")

    @property
    def docs_enabled(self) -> bool:
        if self.ENABLE_DOCS is not None:
            return self.ENABLE_DOCS
        return not self.is_production

    @property
    def json_logs(self) -> bool:
        if self.LOG_JSON is not None:
            return self.LOG_JSON
        return self.is_production

    @property
    def sync_database_url(self) -> str:
        """psycopg URL for Alembic, which runs migrations synchronously."""
        url = self.DATABASE_URL
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+psycopg://", 1)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    @model_validator(mode="after")
    def _enforce_production_hygiene(self) -> "Settings":
        if not self.is_production:
            return self
        problems: list[str] = []
        if self.SECRET_KEY in ("", DEV_SECRET_SENTINEL) or len(self.SECRET_KEY) < 32:
            problems.append("SECRET_KEY must be set to a random value of at least 32 characters")
        if self.HASH_SALT in ("", DEV_SECRET_SENTINEL):
            problems.append("HASH_SALT must be set to a distinct random value")
        if "*" in self.CORS_ORIGINS or not self.cors_origin_list:
            problems.append("CORS_ORIGINS must be an explicit allowlist")
        if not self.COOKIE_SECURE:
            problems.append("COOKIE_SECURE must be true behind HTTPS")
        if "localhost" in self.DATABASE_URL and "sslmode" not in self.DATABASE_URL:
            # localhost is expected on EC2; this is informational only, not fatal.
            pass
        if problems:
            raise ValueError(
                "Refusing to start in "
                f"{self.ENVIRONMENT}: " + "; ".join(problems)
            )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def new_secret() -> str:
    return secrets.token_urlsafe(48)


settings = get_settings()
