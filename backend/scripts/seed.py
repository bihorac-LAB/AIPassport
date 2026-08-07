#!/usr/bin/env python
"""Seed the curriculum tables from backend/content/manifest.json.

    python -m scripts.seed

Safe to run repeatedly: rows are matched by stable key and updated in place. Nothing is deleted.
"""

from __future__ import annotations

import asyncio
import sys

from app.core.db import dispose_engine, get_sessionmaker
from app.core.logging import configure_logging
from app.services.seed import seed_content


async def main() -> int:
    configure_logging()
    async with get_sessionmaker()() as session:
        try:
            report = await seed_content(session)
        except RuntimeError as exc:
            print(f"Seed failed: {exc}", file=sys.stderr)
            return 1
    await dispose_engine()
    print(f"Seed complete: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
