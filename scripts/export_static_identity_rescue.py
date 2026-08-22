#!/usr/bin/env python3
"""Export deterministic API results for the credential-free static demo."""

from __future__ import annotations

import json
import sys
from itertools import permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.identity_rescue.engine import IdentityRescueEngine  # noqa: E402


def main() -> int:
    engine = IdentityRescueEngine()
    analyses: dict[str, object] = {}
    for summary in engine.list_scenarios():
        initial = engine.analyze(summary.scenario_id)
        action_ids = [action.action_id for action in initial.actions]
        for length in range(len(action_ids) + 1):
            for sequence in permutations(action_ids, length):
                key = f"{summary.scenario_id}|{','.join(sequence)}"
                analyses[key] = engine.analyze(
                    summary.scenario_id, list(sequence)
                ).model_dump(mode="json")

    payload = {
        "fixture_version": "1.0",
        "generated_from": "IdentityRescueEngine",
        "deterministic": True,
        "government_systems_contacted": 0,
        "sources": [source.model_dump(mode="json") for source in engine.list_sources()],
        "analyses": analyses,
    }
    target = ROOT / "apps" / "web" / "public" / "identity-rescue-static.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
