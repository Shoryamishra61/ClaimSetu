#!/usr/bin/env python3
"""Initialize SQLite WAL and load the 10×3 fictional reference fixtures."""

from app.config import load_settings
from app.custody import initialise_custody_schema
from app.custody.seed_data import counts
from app.db import Database


def main() -> int:
    settings = load_settings()
    database = Database(settings.database_path)
    database.initialise()
    initialise_custody_schema(database)
    seeded = counts(database)
    print(f"Handover29C SQLite schema verification successful: {seeded}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
