"""Policy engine types.

The engine is deliberately dumb: a list of declarative rules plus pure
evaluator functions over an immutable context. It is a *transparent preflight
representation* of the current Form 29C, not an automated legal eligibility
determination (20_POLICY_MAPPING.md, "Mapping philosophy").

Two things make it auditable:

- every item carries `source_id` + `source_locator` pointing at the primary
  source in 14_SOURCE_LEDGER.md, so the UI can show provenance per row;
- every item declares whether it is fixture-backed, party-declared, or both,
  so the prototype never implies it verified something it only asked about.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum


class SourceType(str, Enum):
    """Where an item's truth actually comes from.

    `SIMULATED_CHECK_WITH_DECLARATION` exists because 20_POLICY_MAPPING.md marks
    RC/PUCC/INSURANCE readiness as "SIMULATED_CHECK/DECLARATION": the fixture
    supplies a document state, and the owner separately declares the document is
    being handed over. Collapsing that into one badge would overstate what the
    prototype knows, so it renders as two badges.
    """

    SIMULATED_CHECK = "SIMULATED_CHECK"
    USER_DECLARATION = "USER_DECLARATION"
    SIMULATED_CHECK_WITH_DECLARATION = "SIMULATED_CHECK_WITH_DECLARATION"
    INFORMATIONAL = "INFORMATIONAL"


class ItemResult(str, Enum):
    PASS = "PASS"
    #: A declaration the party has not yet made. Distinct from FAIL so the UI can
    #: say "you still need to confirm this" rather than "this failed".
    PENDING = "PENDING"
    #: A fixture-backed check that is actively negative (e.g. dealer suspended).
    FAIL = "FAIL"
    #: Informational rows are never pass/fail.
    INFO = "INFO"


class BlockingStage(str, Enum):
    """Which gate an item guards.

    This exists to resolve a real ordering conflict between two source docs.
    20_POLICY_MAPPING.md marks `DEALER_POSSESSION_CONFIRM` as blocking, but
    03_MASTER_PRD.md runs readiness (Step 3) *before* pairing (Step 4), and
    05_UX_UI_INTERACTION_SPEC.md section 7 says the dealer row is only "shown
    when paired". A single boolean would either deadlock preflight before the
    dealer exists, or drop a genuinely required Form 29C declaration.

    So: `PREFLIGHT` items gate entry to shared review; `SUBMIT` items also gate
    submission but not review. Every `PREFLIGHT` item is implicitly also a
    `SUBMIT` item -- preflight failures never become acceptable later.
    """

    PREFLIGHT = "PREFLIGHT"
    SUBMIT = "SUBMIT"
    NONE = "NONE"


class PolicyStage(str, Enum):
    PREFLIGHT = "PREFLIGHT"
    SUBMIT = "SUBMIT"


#: Which actor is expected to satisfy an item, for UI routing.
class ResponsibleActor(str, Enum):
    SELLER = "SELLER"
    DEALER = "DEALER"
    SYSTEM = "SYSTEM"


@dataclass(frozen=True, slots=True)
class PolicyContext:
    """Everything an evaluator is allowed to look at.

    Frozen and explicit so policy evaluation stays a pure function of inputs --
    which is what makes the policy unit tests readable as requirements.
    """

    vehicle_loaded: bool
    dealer_status: str | None
    #: Fixture-supplied document state for the fictional vehicle.
    vehicle_document_flags: dict[str, bool] = field(default_factory=dict)
    #: Declaration code -> value, as recorded against this case.
    declarations: dict[str, bool] = field(default_factory=dict)
    #: True once a dealer has consumed a pair token for this case. Dealer-side
    #: declarations stay PENDING (not FAIL) before that, because the dealer has
    #: not had an opportunity to act yet.
    dealer_joined: bool = False

    def declared(self, code: str) -> bool:
        return self.declarations.get(code) is True

    def document_ready(self, flag: str) -> bool:
        return self.vehicle_document_flags.get(flag) is True


Evaluator = Callable[[PolicyContext], ItemResult]


@dataclass(frozen=True, slots=True)
class PolicyItem:
    code: str
    label_en: str
    label_hi: str
    help_en: str
    help_hi: str
    source_type: SourceType
    responsible: ResponsibleActor
    source_id: str
    source_locator: str
    blocking_stage: BlockingStage
    evaluator: Evaluator

    def blocks_at(self, stage: PolicyStage) -> bool:
        if self.blocking_stage is BlockingStage.NONE:
            return False
        if self.blocking_stage is BlockingStage.PREFLIGHT:
            # A preflight blocker never stops being a blocker.
            return True
        return stage is PolicyStage.SUBMIT


@dataclass(frozen=True, slots=True)
class EvaluatedItem:
    code: str
    label_en: str
    label_hi: str
    help_en: str
    help_hi: str
    source_type: SourceType
    responsible: ResponsibleActor
    source_id: str
    source_locator: str
    blocking_stage: BlockingStage
    #: Whether this item blocks the stage that produced this evaluation.
    blocking: bool
    result: ItemResult


@dataclass(frozen=True, slots=True)
class PolicyEvaluation:
    policy_version: str
    stage: PolicyStage
    passed: bool
    items: tuple[EvaluatedItem, ...]

    @property
    def blocking_failures(self) -> tuple[EvaluatedItem, ...]:
        return tuple(
            i
            for i in self.items
            if i.blocking and i.result is not ItemResult.PASS
        )


@dataclass(frozen=True, slots=True)
class PolicyDefinition:
    """A named, versioned rule set.

    `in_force` is the guard that keeps draft policy out of the running product
    (INV-10 / threat T12). `PolicyService` refuses to select a definition whose
    `in_force` is False, so adding a draft file cannot change product behaviour
    even by misconfiguration.
    """

    version: str
    title: str
    source_id: str
    source_locator: str
    in_force: bool
    items: tuple[PolicyItem, ...]

    def evaluate(
        self, context: PolicyContext, stage: PolicyStage = PolicyStage.PREFLIGHT
    ) -> PolicyEvaluation:
        evaluated: list[EvaluatedItem] = []
        for item in self.items:
            blocking = item.blocks_at(stage)
            evaluated.append(
                EvaluatedItem(
                    code=item.code,
                    label_en=item.label_en,
                    label_hi=item.label_hi,
                    help_en=item.help_en,
                    help_hi=item.help_hi,
                    source_type=item.source_type,
                    responsible=item.responsible,
                    source_id=item.source_id,
                    source_locator=item.source_locator,
                    blocking_stage=item.blocking_stage,
                    blocking=blocking,
                    result=item.evaluator(context),
                )
            )
        passed = all(
            i.result is ItemResult.PASS for i in evaluated if i.blocking
        )
        return PolicyEvaluation(
            policy_version=self.version,
            stage=stage,
            passed=passed,
            items=tuple(evaluated),
        )

    def declaration_codes(self) -> frozenset[str]:
        """Codes a party may set. Fixture-backed checks are not settable."""
        return frozenset(
            i.code
            for i in self.items
            if i.source_type
            in (
                SourceType.USER_DECLARATION,
                SourceType.SIMULATED_CHECK_WITH_DECLARATION,
            )
        )

    def item(self, code: str) -> PolicyItem | None:
        for i in self.items:
            if i.code == code:
                return i
        return None
