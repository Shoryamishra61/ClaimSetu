#!/usr/bin/env python3
"""Run the built SPA and API as one same-origin local review server."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
sys.path.insert(0, str(API_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8129)
    parser.add_argument("--database", default=str(ROOT / "var" / "handover29c.sqlite3"))
    args = parser.parse_args()

    os.environ["H29C_SERVE_FRONTEND"] = "true"
    os.environ["H29C_BUILD_LABEL"] = "local-review"
    os.environ["H29C_DATABASE_PATH"] = args.database

    from app.main import app  # noqa: PLC0415

    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
