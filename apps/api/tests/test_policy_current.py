"""Current-policy preflight behaviour.

Gate G3. Each test knocks out exactly one requirement from the ready state, so a
failure names the requirement that broke.
"""

from __future__ import annotations

from app.domain.policies import registry
from app.domain.policies.cmvr_901e_2022_current import CURRENT_POLICY, POLICY_VERSION
from app.domain.policy_types import (
    BlockingStage,
    ItemResult,
    PolicyStage,
    ResponsibleActor,
    SourceType,
)
from tests.conftest import SELLER_DECLARATION_CODES, ready_context

#: Codes 20_POLICY_MAPPING.md requires the current policy to represent.
MAPPED_CODES = {
    "DEALER_AUTH_ACTIVE",
    "VEHICLE_RECORD_MATCH",
    "RC_READY",
    "PUCC_READY",
    "INSURANCE_READY",
    "TAX_CHALLAN_DECL",
    "PERMIT_DECL",
    "CASE_ACCIDENT_DECL",
    "FINANCE_DECL",
    "SUPERDARI_ENCUMBRANCE_DECL",
    "OWNER_ACCURACY_UNDERTAKING",
    "DEALER_POSSESSION_CONFIRM",
}


class TestPolicyIdentity:
    def test_version_is_the_current_2022_rules(self) -> None:
        assert POLICY_VERSION == "CMVR_901E_2022_CURRENT"

    def test_policy_is_in_force(self) -> None:
        assert CURRENT_POLICY.in_force is True

    def test_registry_current_returns_this_policy(self) -> None:
        assert registry.current().version == POLICY_VERSION

    def test_every_mapped_code_is_present(self) -> None:
        codes = {item.code for item in CURRENT_POLICY.items}
        assert codes >= MAPPED_CODES

    def test_no_unmapped_blocking_codes_were_invented(self) -> None:
        # Anything blocking must trace to 20_POLICY_MAPPING.md. Informational
        # rows may exist beyond the mapping; blockers may not.
        blocking = {
            item.code
            for item in CURRENT_POLICY.items
            if item.blocking_stage is not BlockingStage.NONE
        }
        assert blocking == MAPPED_CODES


class TestProvenance:
    """G3: source provenance attached to each policy item."""

    def test_every_item_names_a_source(self) -> None:
        for item in CURRENT_POLICY.items:
            assert item.source_id, f"{item.code} has no source_id"
            assert item.source_locator, f"{item.code} has no source_locator"

    def test_every_item_has_bilingual_copy(self) -> None:
        for item in CURRENT_POLICY.items:
            assert item.label_en.strip(), f"{item.code} missing label_en"
            assert item.label_hi.strip(), f"{item.code} missing label_hi"
            assert item.help_en.strip(), f"{item.code} missing help_en"
            assert item.help_hi.strip(), f"{item.code} missing help_hi"

    def test_hindi_labels_actually_contain_devanagari(self) -> None:
        # Catches a copy-paste that left English in the Hindi slot.
        for item in CURRENT_POLICY.items:
            assert any(
                "ऀ" <= ch <= "ॿ" for ch in item.label_hi
            ), f"{item.code} label_hi has no Devanagari characters"

    def test_simulated_checks_are_not_attributed_to_the_user(self) -> None:
        for item in CURRENT_POLICY.items:
            if item.source_type is SourceType.SIMULATED_CHECK:
                assert item.responsible is ResponsibleActor.SYSTEM

    def test_declarations_name_a_human_actor(self) -> None:
        for item in CURRENT_POLICY.items:
            if item.source_type is SourceType.USER_DECLARATION:
                assert item.responsible in (
                    ResponsibleActor.SELLER,
                    ResponsibleActor.DEALER,
                )


class TestReadyStatePasses:
    def test_preflight_passes_when_everything_is_ready(self) -> None:
        assert CURRENT_POLICY.evaluate(ready_context()).passed is True

    def test_informational_rows_never_block(self) -> None:
        evaluation = CURRENT_POLICY.evaluate(ready_context())
        for item in evaluation.items:
            if item.source_type is SourceType.INFORMATIONAL:
                assert item.result is ItemResult.INFO
                assert item.blocking is False


class TestBlockers:
    def test_missing_vehicle_blocks(self) -> None:
        assert CURRENT_POLICY.evaluate(ready_context(vehicle_loaded=False)).passed is False

    def test_unverified_dealer_blocks(self) -> None:
        assert CURRENT_POLICY.evaluate(ready_context(dealer_status=None)).passed is False

    def test_expired_dealer_blocks(self) -> None:
        evaluation = CURRENT_POLICY.evaluate(ready_context(dealer_status="EXPIRED"))
        assert evaluation.passed is False
        item = next(i for i in evaluation.items if i.code == "DEALER_AUTH_ACTIVE")
        assert item.result is ItemResult.FAIL

    def test_suspended_dealer_blocks(self) -> None:
        assert (
            CURRENT_POLICY.evaluate(ready_context(dealer_status="SUSPENDED")).passed
            is False
        )

    def test_each_seller_declaration_is_individually_required(self) -> None:
        for code in SELLER_DECLARATION_CODES:
            declarations = {c: True for c in SELLER_DECLARATION_CODES if c != code}
            evaluation = CURRENT_POLICY.evaluate(
                ready_context(declarations=declarations)
            )
            assert evaluation.passed is False, f"{code} was not required"
            item = next(i for i in evaluation.items if i.code == code)
            assert item.result is ItemResult.PENDING

    def test_negative_document_fixture_fails_rather_than_pends(self) -> None:
        # The prototype has positive information the document is not in order, so
        # this is a FAIL the user cannot fix by ticking a box -- distinct from a
        # declaration they simply have not made yet.
        evaluation = CURRENT_POLICY.evaluate(
            ready_context(
                vehicle_document_flags={
                    "rc_ready": True,
                    "pucc_ready": False,
                    "insurance_ready": True,
                }
            )
        )
        assert evaluation.passed is False
        item = next(i for i in evaluation.items if i.code == "PUCC_READY")
        assert item.result is ItemResult.FAIL

    def test_blocking_failures_are_reported_for_the_ui(self) -> None:
        evaluation = CURRENT_POLICY.evaluate(ready_context(dealer_status="EXPIRED"))
        codes = {i.code for i in evaluation.blocking_failures}
        assert "DEALER_AUTH_ACTIVE" in codes


class TestStagedBlocking:
    """The preflight/submit split that resolves the dealer-ordering conflict."""

    def test_dealer_possession_confirm_does_not_block_preflight(self) -> None:
        # Preflight runs before pairing, so requiring the dealer's declaration
        # here would deadlock the journey before the dealer exists.
        evaluation = CURRENT_POLICY.evaluate(
            ready_context(dealer_joined=False), PolicyStage.PREFLIGHT
        )
        assert evaluation.passed is True
        item = next(
            i for i in evaluation.items if i.code == "DEALER_POSSESSION_CONFIRM"
        )
        assert item.blocking is False

    def test_dealer_possession_confirm_blocks_submission(self) -> None:
        evaluation = CURRENT_POLICY.evaluate(
            ready_context(dealer_joined=True), PolicyStage.SUBMIT
        )
        assert evaluation.passed is False
        item = next(
            i for i in evaluation.items if i.code == "DEALER_POSSESSION_CONFIRM"
        )
        assert item.blocking is True
        assert item.result is ItemResult.PENDING

    def test_submission_passes_once_the_dealer_declares(self) -> None:
        declarations = {c: True for c in SELLER_DECLARATION_CODES}
        declarations["DEALER_POSSESSION_CONFIRM"] = True
        evaluation = CURRENT_POLICY.evaluate(
            ready_context(declarations=declarations, dealer_joined=True),
            PolicyStage.SUBMIT,
        )
        assert evaluation.passed is True

    def test_preflight_blockers_still_block_at_submit(self) -> None:
        declarations = {c: True for c in SELLER_DECLARATION_CODES}
        declarations["DEALER_POSSESSION_CONFIRM"] = True
        evaluation = CURRENT_POLICY.evaluate(
            ready_context(
                declarations=declarations,
                dealer_joined=True,
                dealer_status="EXPIRED",
            ),
            PolicyStage.SUBMIT,
        )
        assert evaluation.passed is False

    def test_dealer_declaration_pends_rather_than_fails_before_join(self) -> None:
        # Calling it a failure would push the seller to "fix" something that is
        # not broken -- the dealer simply has not had a turn yet.
        evaluation = CURRENT_POLICY.evaluate(ready_context(dealer_joined=False))
        item = next(
            i for i in evaluation.items if i.code == "DEALER_POSSESSION_CONFIRM"
        )
        assert item.result is ItemResult.PENDING


class TestDeclarationCodes:
    def test_fixture_only_checks_are_not_user_settable(self) -> None:
        settable = CURRENT_POLICY.declaration_codes()
        assert "DEALER_AUTH_ACTIVE" not in settable
        assert "VEHICLE_RECORD_MATCH" not in settable
        assert "RULE_55C_EFFECT_INFO" not in settable

    def test_hybrid_document_rows_are_settable(self) -> None:
        settable = CURRENT_POLICY.declaration_codes()
        assert {"RC_READY", "PUCC_READY", "INSURANCE_READY"} <= settable


class TestPurity:
    def test_evaluation_does_not_mutate_the_context(self) -> None:
        context = ready_context()
        before = dict(context.declarations)
        CURRENT_POLICY.evaluate(context)
        assert context.declarations == before

    def test_repeated_evaluation_is_stable(self) -> None:
        context = ready_context()
        first = CURRENT_POLICY.evaluate(context)
        second = CURRENT_POLICY.evaluate(context)
        assert [(i.code, i.result) for i in first.items] == [
            (i.code, i.result) for i in second.items
        ]
