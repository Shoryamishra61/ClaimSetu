"""Draft 2026 policy must be documented but inert.

Gate G0 ("2026 draft cannot execute"), INV-10, threat T12, and test T25
("current policy config points to draft -> CI fails").
"""

from __future__ import annotations

import pytest

from app.domain.policies import registry
from app.domain.policies.draft.gsr_649e_2026_draft import (
    ALLOWED_WORDING_EN,
    DRAFT_POLICY,
    PROPOSED_CHANGES,
)
from app.domain.policies.draft.gsr_649e_2026_draft import (
    POLICY_VERSION as DRAFT_VERSION,
)


class TestDraftIsNotInForce:
    def test_draft_declares_itself_not_in_force(self) -> None:
        assert DRAFT_POLICY.in_force is False

    def test_draft_title_says_draft(self) -> None:
        assert "DRAFT" in DRAFT_POLICY.title.upper()

    def test_draft_has_no_evaluable_items(self) -> None:
        # Writing speculative evaluators for draft text would be improvising law.
        assert DRAFT_POLICY.items == ()

    def test_draft_version_is_distinct_from_the_current_version(self) -> None:
        assert DRAFT_VERSION != registry.CURRENT_POLICY_VERSION


class TestDraftIsNotSelectable:
    def test_draft_is_absent_from_the_selectable_registry(self) -> None:
        assert DRAFT_VERSION not in registry.SELECTABLE

    def test_asking_for_the_draft_raises(self) -> None:
        with pytest.raises(registry.PolicyNotSelectable):
            registry.get(DRAFT_VERSION)

    def test_only_the_current_policy_is_selectable(self) -> None:
        assert set(registry.SELECTABLE) == {"CMVR_901E_2022_CURRENT"}

    def test_every_selectable_policy_is_in_force(self) -> None:
        # Defence in depth: even a mistaken registry entry cannot run.
        for definition in registry.SELECTABLE.values():
            assert definition.in_force is True

    def test_a_not_in_force_definition_is_refused_even_if_registered(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Simulates the misconfiguration this guard exists for.
        monkeypatch.setitem(registry.SELECTABLE, DRAFT_VERSION, DRAFT_POLICY)
        with pytest.raises(registry.PolicyNotSelectable, match="not in force"):
            registry.get(DRAFT_VERSION)


class TestProductionConfigPointsAtCurrentLaw:
    def test_current_policy_version_constant_is_the_2022_rules(self) -> None:
        assert registry.CURRENT_POLICY_VERSION == "CMVR_901E_2022_CURRENT"

    def test_current_returns_an_in_force_definition(self) -> None:
        assert registry.current().in_force is True


class TestAllowedWording:
    def test_allowed_wording_calls_the_rules_draft(self) -> None:
        lowered = ALLOWED_WORDING_EN.lower()
        assert "draft" in lowered
        assert "not executed" in lowered

    def test_allowed_wording_does_not_assert_a_current_requirement(self) -> None:
        # Forbidden framing per claims ledger section E: "From July 2026 the law
        # requires Form 29CA...".
        lowered = ALLOWED_WORDING_EN.lower()
        assert "the law requires" not in lowered
        assert "is required" not in lowered

    def test_proposed_changes_are_recorded_as_proposals(self) -> None:
        assert PROPOSED_CHANGES
        for line in PROPOSED_CHANGES:
            assert line.strip()

    def test_form_29ca_appears_only_as_a_proposal(self) -> None:
        # It may be named in the draft record; it must not exist as a workflow.
        assert any("29CA" in line for line in PROPOSED_CHANGES)
