"""Simulated authorised-dealer (Form 29B) registry.

Reads ``fixtures/dealers.json``. Stands in for the Rule 55A / Form 29B
authorisation state. It is not a copy of, feed from, or lookup against any
government register.

The ``purpose`` argument on ``lookup`` is what makes threat T06 ("dealer status
changes between verification and submit") demonstrable. A fixture may declare a
``simulated_revalidation_status``; when the SubmissionService rechecks with
``purpose=REVALIDATION``, that status is returned instead. This is a declared
property of a declared simulation, named on the demo scenario card -- not a hidden
switch.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .fixture_loader import load
from .simulation import SimulatedResponse, TruthLabel


class DealerStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    SUSPENDED = "SUSPENDED"
    NOT_FOUND = "NOT_FOUND"


#: The one status that allows the journey to continue. Everything else blocks.
CONTINUABLE_STATUSES: frozenset[DealerStatus] = frozenset({DealerStatus.ACTIVE})


class LookupPurpose(str, Enum):
    #: Seller is checking the dealer on screen 2.
    VERIFICATION = "VERIFICATION"
    #: SubmissionService rechecking immediately before submit (INV-04).
    REVALIDATION = "REVALIDATION"


#: Plain-language explanation per status. Blocking copy must explain *why* a
#: dealer cannot continue, not just that they cannot.
STATUS_TEXT_EN: dict[DealerStatus, str] = {
    DealerStatus.ACTIVE: (
        "This dealer is shown as currently authorised in the simulated registry."
    ),
    DealerStatus.EXPIRED: (
        "This dealer's authorisation period has ended in the simulated registry. "
        "Rule 55A requires a valid authorisation, so this handover cannot continue."
    ),
    DealerStatus.SUSPENDED: (
        "This dealer's authorisation is suspended in the simulated registry, so "
        "this handover cannot continue."
    ),
    DealerStatus.NOT_FOUND: (
        "No dealer with this authorisation number exists in the simulated "
        "registry. Check the number, or use the demo dealer."
    ),
}

STATUS_TEXT_HI: dict[DealerStatus, str] = {
    DealerStatus.ACTIVE: (
        "सिम्युलेटेड रजिस्ट्री में यह डीलर वर्तमान में प्राधिकृत दिखाया गया है।"
    ),
    DealerStatus.EXPIRED: (
        "सिम्युलेटेड रजिस्ट्री में इस डीलर के प्राधिकरण की अवधि समाप्त हो गई है। "
        "नियम 55A के अनुसार वैध प्राधिकरण आवश्यक है, इसलिए यह हस्तांतरण आगे नहीं बढ़ सकता।"
    ),
    DealerStatus.SUSPENDED: (
        "सिम्युलेटेड रजिस्ट्री में इस डीलर का प्राधिकरण निलंबित है, इसलिए यह हस्तांतरण "
        "आगे नहीं बढ़ सकता।"
    ),
    DealerStatus.NOT_FOUND: (
        "इस प्राधिकरण संख्या वाला कोई डीलर सिम्युलेटेड रजिस्ट्री में नहीं है। संख्या जाँचें, "
        "या डेमो डीलर का उपयोग करें।"
    ),
}


@dataclass(frozen=True, slots=True)
class DealerRecord(SimulatedResponse):
    id: str
    authorisation_no: str
    business_name: str
    status: DealerStatus
    valid_from: str
    valid_until: str
    is_default_demo: bool
    demo_label_en: str
    demo_label_hi: str

    @property
    def can_continue(self) -> bool:
        return self.status in CONTINUABLE_STATUSES


@dataclass(frozen=True, slots=True)
class DealerNotFound(SimulatedResponse):
    """A miss is still a registry answer, so it still carries a truth label."""

    authorisation_no: str
    status: DealerStatus = DealerStatus.NOT_FOUND

    @property
    def can_continue(self) -> bool:
        return False


def _normalise(value: str) -> str:
    return "".join(value.split()).upper()


class MockDealerRegistry:
    def __init__(self) -> None:
        rows = load("dealers.json")["dealers"]
        self._rows: dict[str, dict] = {
            _normalise(row["authorisation_no"]): row for row in rows
        }

    def all(self) -> tuple[DealerRecord, ...]:
        return tuple(
            self._to_record(row, DealerStatus(row["status"]))
            for row in self._rows.values()
        )

    def default_demo(self) -> DealerRecord:
        for row in self._rows.values():
            if row["is_default_demo"]:
                return self._to_record(row, DealerStatus(row["status"]))
        raise RuntimeError(
            "dealers.json must mark exactly one record as is_default_demo"
        )

    def lookup(
        self,
        *,
        authorisation_no: str,
        purpose: LookupPurpose = LookupPurpose.VERIFICATION,
    ) -> DealerRecord | DealerNotFound:
        row = self._rows.get(_normalise(authorisation_no))
        if row is None:
            return DealerNotFound(
                truth_label=TruthLabel.SIMULATED_AUTHORISED_DEALER_REGISTRY,
                authorisation_no=authorisation_no,
            )

        status = DealerStatus(row["status"])
        if purpose is LookupPurpose.REVALIDATION:
            override = row.get("simulated_revalidation_status")
            if override:
                status = DealerStatus(override)
        return self._to_record(row, status)

    def _to_record(self, row: dict, status: DealerStatus) -> DealerRecord:
        return DealerRecord(
            truth_label=TruthLabel.SIMULATED_AUTHORISED_DEALER_REGISTRY,
            id=row["id"],
            authorisation_no=row["authorisation_no"],
            business_name=row["business_name"],
            status=status,
            valid_from=row["valid_from"],
            valid_until=row["valid_until"],
            is_default_demo=bool(row["is_default_demo"]),
            demo_label_en=row["demo_label_en"],
            demo_label_hi=row["demo_label_hi"],
        )
