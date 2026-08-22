"""Canonical payload serialisation and hashing.

Two kinds of test here:

1.  **Property tests** — assert the behaviour the hash exists to provide:
    order-independence where order is meaningless, and sensitivity to every field
    that is part of what the parties agreed to.

2.  **A locked vector** — pins the exact bytes and digest so the serialisation
    cannot drift silently. A drift would invalidate every confirmation already
    recorded, so it must be a loud, deliberate change.

The vector file is generated once by ``scripts/lock_canonical_vector.py`` and
committed. Until it exists, ``test_locked_vector_matches`` FAILS rather than
skips: a skipped test reads as green in CI, and this is exactly the guard that
must not be silently absent.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from app.domain.canonical import (
    CANONICAL_SCHEMA_VERSION,
    CanonicalDealer,
    CanonicalDeclaration,
    CanonicalPayload,
    CanonicalVehicle,
    canonical_json,
    payload_hash,
)

VECTOR_PATH = Path(__file__).parent / "vectors" / "canonical_v1.json"

#: The reference payload. Values are fixed literals -- no clock, no uuid -- so
#: the vector is reproducible on any machine at any time.
REFERENCE = CanonicalPayload(
    case_id="00000000-0000-4000-8000-000000000001",
    policy_version="CMVR_901E_2022_CURRENT",
    vehicle=CanonicalVehicle(
        registration_no="DEMO01AB1234", chassis_suffix="12345"
    ),
    dealer=CanonicalDealer(
        authorisation_no="DEMO-29B-001",
        business_name="Asha Motors (fictional dealer)",
    ),
    declarations=(
        CanonicalDeclaration(code="RC_READY", value=True),
        CanonicalDeclaration(code="PUCC_READY", value=True),
        CanonicalDeclaration(code="INSURANCE_READY", value=True),
        CanonicalDeclaration(code="TAX_CHALLAN_DECL", value=True),
    ),
    handover_local_time="2026-08-22T10:30:00+05:30",
    registered_owner_name="Ramesh Kumar (fictional)",
)


class TestDeterminism:
    def test_same_payload_hashes_identically(self) -> None:
        assert payload_hash(REFERENCE) == payload_hash(REFERENCE)

    def test_declaration_order_does_not_affect_the_hash(self) -> None:
        # The order a user happened to tick boxes in is not part of the
        # agreement, so it must not change the hash.
        shuffled = replace(
            REFERENCE, declarations=tuple(reversed(REFERENCE.declarations))
        )
        assert payload_hash(shuffled) == payload_hash(REFERENCE)

    def test_hash_is_lowercase_hex_sha256(self) -> None:
        digest = payload_hash(REFERENCE)
        assert len(digest) == 64
        assert digest == digest.lower()
        assert all(c in "0123456789abcdef" for c in digest)

    def test_canonical_json_has_no_incidental_whitespace(self) -> None:
        serialised = canonical_json(REFERENCE)
        assert ", " not in serialised
        assert ": " not in serialised

    def test_canonical_json_keys_are_sorted(self) -> None:
        parsed = json.loads(canonical_json(REFERENCE))
        assert list(parsed) == sorted(parsed)

    def test_schema_version_is_embedded(self) -> None:
        # So a stored hash can always be traced to the routine that produced it.
        assert CANONICAL_SCHEMA_VERSION in canonical_json(REFERENCE)


class TestMutationSensitivity:
    """INV-03: any change to what the parties agreed must change the hash."""

    def test_changing_the_registration_number_changes_the_hash(self) -> None:
        mutated = replace(
            REFERENCE,
            vehicle=replace(REFERENCE.vehicle, registration_no="DEMO02CD5678"),
        )
        assert payload_hash(mutated) != payload_hash(REFERENCE)

    def test_changing_the_chassis_suffix_changes_the_hash(self) -> None:
        mutated = replace(
            REFERENCE, vehicle=replace(REFERENCE.vehicle, chassis_suffix="99999")
        )
        assert payload_hash(mutated) != payload_hash(REFERENCE)

    def test_changing_the_dealer_changes_the_hash(self) -> None:
        mutated = replace(
            REFERENCE,
            dealer=replace(REFERENCE.dealer, authorisation_no="DEMO-29B-004"),
        )
        assert payload_hash(mutated) != payload_hash(REFERENCE)

    def test_changing_the_owner_name_changes_the_hash(self) -> None:
        mutated = replace(REFERENCE, registered_owner_name="Someone Else (fictional)")
        assert payload_hash(mutated) != payload_hash(REFERENCE)

    def test_changing_the_handover_time_changes_the_hash(self) -> None:
        mutated = replace(REFERENCE, handover_local_time="2026-08-23T10:30:00+05:30")
        assert payload_hash(mutated) != payload_hash(REFERENCE)

    def test_flipping_a_declaration_changes_the_hash(self) -> None:
        flipped = tuple(
            replace(d, value=False) if d.code == "RC_READY" else d
            for d in REFERENCE.declarations
        )
        assert payload_hash(replace(REFERENCE, declarations=flipped)) != payload_hash(
            REFERENCE
        )

    def test_removing_a_declaration_changes_the_hash(self) -> None:
        fewer = REFERENCE.declarations[:-1]
        assert payload_hash(replace(REFERENCE, declarations=fewer)) != payload_hash(
            REFERENCE
        )

    def test_changing_the_policy_version_changes_the_hash(self) -> None:
        # A confirmation is against a payload evaluated under a specific policy
        # version; the version is therefore part of the agreement.
        mutated = replace(REFERENCE, policy_version="SOMETHING_ELSE")
        assert payload_hash(mutated) != payload_hash(REFERENCE)

    def test_changing_the_case_id_changes_the_hash(self) -> None:
        # Prevents a confirmation recorded on one case from validating another.
        mutated = replace(REFERENCE, case_id="00000000-0000-4000-8000-000000000002")
        assert payload_hash(mutated) != payload_hash(REFERENCE)


class TestPresentationIndependence:
    def test_canonical_dict_contains_no_presentation_fields(self) -> None:
        # Re-wording a label or translating the UI must not invalidate an
        # existing confirmation, so no label/translation may be in the payload.
        serialised = canonical_json(REFERENCE)
        for forbidden in ("label", "label_en", "label_hi", "help", "badge", "truth"):
            assert forbidden not in serialised

    def test_canonical_dict_field_set_is_closed(self) -> None:
        # Adding a field is a breaking change; this test forces the author to
        # come here and think about the schema version.
        assert set(REFERENCE.to_canonical_dict()) == {
            "schema_version",
            "policy_version",
            "case_id",
            "vehicle",
            "registered_owner_name",
            "dealer",
            "declarations",
            "handover_local_time",
        }


class TestLockedVector:
    def test_locked_vector_matches(self) -> None:
        if not VECTOR_PATH.exists():
            pytest.fail(
                "Canonical hash vector is not locked yet.\n"
                f"Expected file: {VECTOR_PATH}\n"
                "Generate it once with:\n"
                "    python scripts/lock_canonical_vector.py\n"
                "then commit it. This test fails rather than skips on purpose: a "
                "skipped serialisation guard reads as green in CI."
            )
        vector = json.loads(VECTOR_PATH.read_text(encoding="utf-8"))
        assert vector["schema_version"] == CANONICAL_SCHEMA_VERSION
        assert canonical_json(REFERENCE) == vector["canonical_json"]
        assert payload_hash(REFERENCE) == vector["sha256"]
