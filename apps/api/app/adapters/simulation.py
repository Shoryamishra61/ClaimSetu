"""Simulation envelope shared by every mock adapter.

02_EVIDENCE_AND_CLAIMS_LEDGER.md section D fixes the exact set of truth labels a
government-shaped object may carry. They are constants here so that no adapter
can invent a friendlier-sounding label, and so a contract test can assert the
set is closed.

INV-07: every government-shaped adapter response carries ``simulation=True``.
``simulation`` is not a mutable field with a default -- it is a property that
always returns True. There is no code path that can produce a response object
claiming to be real.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TruthLabel(str, Enum):
    SIMULATED_GOVERNMENT_RESPONSE = "SIMULATED GOVERNMENT RESPONSE"
    FICTIONAL_VEHICLE_DATA = "FICTIONAL VEHICLE DATA"
    SIMULATED_AUTHORISED_DEALER_REGISTRY = "SIMULATED AUTHORISED-DEALER REGISTRY"
    SIMULATED_FORM_29C_SUBMISSION = "SIMULATED FORM 29C SUBMISSION"


@dataclass(frozen=True, slots=True)
class SimulatedResponse:
    """Base for every adapter DTO that is shaped like a government response.

    Subclasses add payload fields. They must not override ``simulation``.
    """

    truth_label: TruthLabel

    @property
    def simulation(self) -> bool:
        # A property, not a field: there is deliberately no way to construct one
        # of these with simulation=False.
        return True

    def envelope(self) -> dict[str, object]:
        return {"simulation": self.simulation, "truth_label": self.truth_label.value}
