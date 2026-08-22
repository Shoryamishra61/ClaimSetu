"""Fixture file loading.

Read-only. Loaded once and cached, because the fixtures are the deterministic
substrate the whole demo rests on -- re-reading them mid-run would let a file edit
change behaviour between two steps of the same journey.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Any


def fixtures_dir() -> Path:
    """Locate the repository ``fixtures/`` directory.

    Walks up from this module rather than trusting the process working directory,
    so tests, the dev server and a container all resolve the same files.
    """
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "fixtures"
        if candidate.is_dir() and (candidate / "vehicles.json").is_file():
            return candidate
    raise FileNotFoundError(
        "Could not locate the fixtures/ directory containing vehicles.json "
        f"by walking up from {here}"
    )


@cache
def load(name: str) -> dict[str, Any]:
    path = fixtures_dir() / name
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
