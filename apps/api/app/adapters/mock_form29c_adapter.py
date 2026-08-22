"""Simulated Form 29C submission boundary.

This is the **only** government boundary in P0 (blueprint section 7). It exists as
a replaceable interface so that a future, formally approved sandbox could be
substituted without touching domain logic -- not because any such integration is
planned or permitted here.

What it is not: it does not call anything, it has no network dependency, and it
does not create a Form 29C record anywhere. It returns a deterministic outcome
derived from the chosen fictional vehicle's ``submission_scenario``.

Determinism rule (09_QA_TEST_DEMO_RELIABILITY.md section 6): the outcome is a
pure function of (scenario, attempt_number). Nothing is random. A judge who picks
DEMO03EF9012 gets UNKNOWN every single time, and there is no switch that turns
that into success.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import ClassVar

from .simulation import SimulatedResponse, TruthLabel


class SubmissionOutcome(str, Enum):
    ACK = "ACK"
    REJECTED = "REJECTED"
    TEMPORARY_FAILURE = "TEMPORARY_FAILURE"
    UNKNOWN = "UNKNOWN"


class ReasonCode(str, Enum):
    DEALER_AUTH_EXPIRED = "DEALER_AUTH_EXPIRED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UPSTREAM_TIMEOUT = "UPSTREAM_TIMEOUT"


#: Plain-language explanation per reason code. The UI must never show the raw
#: code as the primary message (UX quality bar: no internal jargon).
REASON_TEXT_EN: dict[ReasonCode, str] = {
    ReasonCode.DEALER_AUTH_EXPIRED: (
        "The simulated registry reported that the dealer's authorisation is no "
        "longer active."
    ),
    ReasonCode.VALIDATION_ERROR: (
        "The simulated portal rejected the handover details as incomplete or "
        "inconsistent."
    ),
    ReasonCode.UPSTREAM_TIMEOUT: (
        "The simulated portal did not respond in time, so no acknowledgement was "
        "issued."
    ),
}

REASON_TEXT_HI: dict[ReasonCode, str] = {
    ReasonCode.DEALER_AUTH_EXPIRED: (
        "सिम्युलेटेड रजिस्ट्री ने बताया कि डीलर का प्राधिकरण अब सक्रिय नहीं है।"
    ),
    ReasonCode.VALIDATION_ERROR: (
        "सिम्युलेटेड पोर्टल ने हस्तांतरण विवरण को अपूर्ण या असंगत बताकर अस्वीकार कर दिया।"
    ),
    ReasonCode.UPSTREAM_TIMEOUT: (
        "सिम्युलेटेड पोर्टल ने समय पर उत्तर नहीं दिया, इसलिए कोई पावती जारी नहीं हुई।"
    ),
}


@dataclass(frozen=True, slots=True)
class Form29CSubmissionResponse(SimulatedResponse):
    status: SubmissionOutcome
    acknowledgement_no: str | None
    reason_code: ReasonCode | None
    submitted_at: str
    #: Makes the signature boundary explicit in debug/source metadata, as
    #: 04_SOFTWARE_REQUIREMENTS_SPEC.md section 17 requires. The app's confirm
    #: action is not an e-signature; official signing would happen here.
    official_signature_simulated: bool = True

    def __post_init__(self) -> None:
        # An acknowledgement number exists if and only if the outcome is ACK.
        # Enforced at construction so no downstream code has to trust a caller.
        if self.status is SubmissionOutcome.ACK:
            if not self.acknowledgement_no:
                raise ValueError("ACK response must carry an acknowledgement number")
            if self.reason_code is not None:
                raise ValueError("ACK response must not carry a reason code")
        else:
            if self.acknowledgement_no:
                raise ValueError(
                    f"{self.status.value} response must not carry an "
                    "acknowledgement number"
                )


class MockForm29CAdapter:
    """Deterministic stand-in for the official Form 29C submission surface.

    ``attempt_number`` is 1-based and lets a scenario evolve across retries
    without any randomness or wall-clock dependency. Only one scenario uses it:
    ``UNKNOWN_THEN_ACK`` models the real-world case where the first response is
    lost but the submission actually landed upstream, which is exactly the case
    that status reconciliation exists for.
    """

    #: Fixture scenario string -> outcome sequence by attempt number.
    _SCENARIOS: ClassVar[dict[str, tuple[SubmissionOutcome, ...]]] = {
        "ACK": (SubmissionOutcome.ACK,),
        "REJECTED": (SubmissionOutcome.REJECTED,),
        "TEMPORARY_FAILURE": (SubmissionOutcome.TEMPORARY_FAILURE,),
        "UNKNOWN": (SubmissionOutcome.UNKNOWN,),
        "UNKNOWN_THEN_ACK": (SubmissionOutcome.UNKNOWN, SubmissionOutcome.ACK),
    }

    _REASON_FOR: ClassVar[dict[SubmissionOutcome, ReasonCode | None]] = {
        SubmissionOutcome.ACK: None,
        SubmissionOutcome.REJECTED: ReasonCode.VALIDATION_ERROR,
        SubmissionOutcome.TEMPORARY_FAILURE: ReasonCode.UPSTREAM_TIMEOUT,
        SubmissionOutcome.UNKNOWN: ReasonCode.UPSTREAM_TIMEOUT,
    }

    def __init__(self, *, ack_prefix: str = "SIM29C") -> None:
        self._ack_prefix = ack_prefix

    def known_scenarios(self) -> frozenset[str]:
        return frozenset(self._SCENARIOS)

    def submit(
        self,
        *,
        scenario: str,
        case_id: str,
        payload_hash: str,
        attempt_number: int = 1,
        now: datetime | None = None,
    ) -> Form29CSubmissionResponse:
        """Return the deterministic outcome for this scenario and attempt.

        ``payload_hash`` is accepted so the acknowledgement number is a stable
        function of the exact payload that was submitted: resubmitting the same
        payload yields the same number, which is what makes the idempotency
        guarantee visible end-to-end rather than only in the database.
        """
        sequence = self._SCENARIOS.get(scenario)
        if sequence is None:
            raise ValueError(
                f"Unknown simulated scenario {scenario!r}. "
                f"Known: {sorted(self._SCENARIOS)}"
            )
        index = min(max(attempt_number, 1) - 1, len(sequence) - 1)
        outcome = sequence[index]

        moment = now or datetime.now(timezone.utc)
        return Form29CSubmissionResponse(
            truth_label=TruthLabel.SIMULATED_FORM_29C_SUBMISSION,
            status=outcome,
            acknowledgement_no=(
                self._acknowledgement_no(payload_hash)
                if outcome is SubmissionOutcome.ACK
                else None
            ),
            reason_code=self._REASON_FOR[outcome],
            submitted_at=moment.isoformat(),
        )

    def _acknowledgement_no(self, payload_hash: str) -> str:
        # Derived from the payload hash so it is deterministic and reproducible in
        # tests, and so the same payload always yields the same number. The
        # SIM prefix keeps it visibly non-official.
        return f"{self._ack_prefix}-2026-{payload_hash[:8].upper()}"
