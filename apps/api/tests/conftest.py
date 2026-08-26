"""Shared test fixtures.

Two layers of helper live here, and the split is deliberate.

The *pure* helpers (`ready_context`, the declaration code tuples) exist because the
domain layer has no I/O, so policy and state tests need no database at all.

The *driver* (`Journey`) exists because almost every invariant test needs a case in
a specific state, and hand-rolling the walk to that state in each test would mean
that a bug in the walk shows up as twenty unrelated failures. One driver, one place
to fix. `Journey` deliberately calls the **services**, not HTTP: the invariants must
hold for any caller, and a test that could only reach them through FastAPI would not
prove that.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from app.adapters.mock_dealer_registry import MockDealerRegistry
from app.adapters.mock_form29c_adapter import MockForm29CAdapter
from app.adapters.mock_vehicle_registry import MockVehicleRegistry
from app.config import Settings
from app.domain.policies import registry
from app.domain.policy_types import PolicyContext
from app.domain.states import Actor
from app.services.case_service import CaseService
from app.services.confirmation_service import ConfirmationService
from app.services.context import ServiceContext
from app.services.pairing_service import PairingService
from app.services.projection import CaseView
from app.services.submission_service import SubmissionResult, SubmissionService


@pytest.fixture(scope="session")
def vehicles() -> MockVehicleRegistry:
    return MockVehicleRegistry()


@pytest.fixture(scope="session")
def dealers() -> MockDealerRegistry:
    return MockDealerRegistry()


@pytest.fixture(scope="session")
def adapter() -> MockForm29CAdapter:
    return MockForm29CAdapter()


#: Every seller-side declaration code in the current policy. Used by tests that
#: need a "seller has done everything" context without listing codes inline.
SELLER_DECLARATION_CODES = (
    "RC_READY",
    "PUCC_READY",
    "INSURANCE_READY",
    "TAX_CHALLAN_DECL",
    "PERMIT_DECL",
    "CASE_ACCIDENT_DECL",
    "FINANCE_DECL",
    "SUPERDARI_ENCUMBRANCE_DECL",
    "OWNER_ACCURACY_UNDERTAKING",
)

#: The dealer's own blocking item. Staged at SUBMIT rather than PREFLIGHT, which is
#: why the driver sets it only after the dealer has joined -- see the BlockingStage
#: docstring in domain/policy_types.py.
DEALER_DECLARATION_CODES = ("DEALER_POSSESSION_CONFIRM",)


def ready_context(**overrides) -> PolicyContext:
    """A context in which current-policy preflight passes.

    Tests then knock out one thing at a time, so a failure names exactly which
    requirement broke.
    """
    base = {
        "vehicle_loaded": True,
        "dealer_status": "ACTIVE",
        "vehicle_document_flags": {
            "rc_ready": True,
            "pucc_ready": True,
            "insurance_ready": True,
        },
        "declarations": {code: True for code in SELLER_DECLARATION_CODES},
        "dealer_joined": False,
    }
    base.update(overrides)
    return PolicyContext(**base)


# ---------------------------------------------------------------------------
# stateful fixtures
# ---------------------------------------------------------------------------

#: The happy-path fixture pair. Named constants so a test that needs the rejection
#: or unknown scenario has to say so explicitly, rather than differing from the
#: default by one silent character.
DEFAULT_VEHICLE = ("DEMO01AB1234", "12345")
DEFAULT_DEALER = "DEMO-29B-001"


@pytest.fixture()
def settings(tmp_path) -> Settings:
    """A throwaway on-disk database per test.

    A file rather than ``:memory:`` because ``Database`` opens a connection per
    transaction; an in-memory database would be empty on every call. The file also
    means a test can drop and rebuild ``ServiceContext`` to simulate a process
    restart, which is how refresh-safety is actually proven.
    """
    return Settings(
        database_path=str(tmp_path / "handover29c-test.sqlite3"),
        policy_version=registry.CURRENT_POLICY_VERSION,
        pair_token_ttl_seconds=300,
        pair_token_bytes=32,
        cors_origins=(),
        build_label="test",
        poll_interval_seconds=2.0,
        serve_frontend=False,
        # Zero, so the suite does not spend real seconds waiting on a simulation of
        # latency. The two-phase submit is still two phases; only the sleep is gone.
        simulated_adapter_latency_ms=0,
        # The large regression suite covers the quarantined research controller.
        # load_settings() and the Docker runtime leave this false.
        enable_historical_blueprint=True,
    )


@pytest.fixture()
def ctx(settings: Settings) -> ServiceContext:
    return ServiceContext.build(settings)


class Journey:
    """Walks a case through the flow by calling services directly.

    Every method returns the resulting ``CaseView`` so a test can assert on state
    without a second lookup. Tokens are held here because a test that had to thread
    two opaque strings through eight calls would be mostly plumbing.
    """

    def __init__(self, ctx: ServiceContext) -> None:
        self.ctx = ctx
        self.cases = CaseService(ctx)
        self.confirmations = ConfirmationService(ctx)
        self.submissions = SubmissionService(ctx)
        # One instance for the whole journey, because its rate-limit windows are
        # in-process state -- the same reason main.py keeps a process singleton.
        self.pairing = PairingService(ctx)
        self.case_id: str = ""
        self.seller_token: str = ""
        self.dealer_token: str = ""
        self.pair_code: str = ""

    # -- setup -----------------------------------------------------------------

    def create(
        self, journey_type: str = "AUTHORISED_DEALER_HANDOFF"
    ) -> CaseView:
        created = self.cases.create_case(journey_type=journey_type)
        self.case_id = created.view.case.id
        self.seller_token = created.seller_token
        return created.view

    def verify_vehicle(
        self, registration_no: str | None = None, chassis_suffix: str | None = None
    ) -> CaseView:
        reg, chassis = DEFAULT_VEHICLE
        return self.cases.verify_vehicle(
            case_id=self.case_id,
            token=self.seller_token,
            registration_no=registration_no or reg,
            chassis_suffix=chassis_suffix or chassis,
        )

    def verify_dealer(self, authorisation_no: str = DEFAULT_DEALER) -> CaseView:
        return self.cases.verify_dealer(
            case_id=self.case_id,
            token=self.seller_token,
            authorisation_no=authorisation_no,
        )

    def seller_declarations(self, **overrides: bool) -> CaseView:
        values = {code: True for code in SELLER_DECLARATION_CODES}
        values.update(overrides)
        return self.cases.set_declarations(
            case_id=self.case_id, token=self.seller_token, values=values
        )

    def dealer_declarations(self, **overrides: bool) -> CaseView:
        values = {code: True for code in DEALER_DECLARATION_CODES}
        values.update(overrides)
        return self.cases.set_declarations(
            case_id=self.case_id, token=self.dealer_token, values=values
        )

    # -- pairing ---------------------------------------------------------------

    def pair(self) -> str:
        issued = self.pairing.issue_code(
            case_id=self.case_id, token=self.seller_token
        )
        self.pair_code = issued.code
        return issued.code

    def join(self, code: str | None = None, client_key: str = "test-client") -> CaseView:
        redeemed = self.pairing.redeem(
            code=code or self.pair_code, client_key=client_key
        )
        self.dealer_token = redeemed.dealer_token
        return redeemed.view

    # -- confirmation ----------------------------------------------------------

    def token_for(self, actor: Actor) -> str:
        return self.seller_token if actor is Actor.SELLER else self.dealer_token

    def payload_hash(self) -> str:
        return self.view().case.payload_hash or ""

    def confirm(self, actor: Actor, payload_hash: str | None = None) -> CaseView:
        result = self.confirmations.confirm(
            case_id=self.case_id,
            token=self.token_for(actor),
            payload_hash_claim=payload_hash or self.payload_hash(),
        )
        return result.view

    def withdraw(self, actor: Actor) -> CaseView:
        return self.confirmations.withdraw(
            case_id=self.case_id, token=self.token_for(actor)
        ).view

    # -- submission ------------------------------------------------------------

    def submit(
        self,
        *,
        idempotency_key: str = "test-key-1",
        payload_hash: str | None = None,
        actor: Actor = Actor.SELLER,
    ) -> SubmissionResult:
        return self.submissions.submit(
            case_id=self.case_id,
            token=self.token_for(actor),
            payload_hash_claim=payload_hash or self.payload_hash(),
            idempotency_key=idempotency_key,
        )

    def reconcile(self, actor: Actor = Actor.SELLER) -> SubmissionResult:
        return self.submissions.reconcile(
            case_id=self.case_id, token=self.token_for(actor)
        )

    # -- reads -----------------------------------------------------------------

    def view(self) -> CaseView:
        return self.cases.snapshot(case_id=self.case_id)

    def audit_types(self) -> list[str]:
        return [e.event_type for e in self.cases.audit_trail(case_id=self.case_id)]

    # -- composite walks -------------------------------------------------------

    def to_preflight_passed(
        self,
        *,
        vehicle: tuple[str, str] | None = None,
        dealer: str = DEFAULT_DEALER,
    ) -> CaseView:
        self.create()
        reg, chassis = vehicle or DEFAULT_VEHICLE
        self.verify_vehicle(reg, chassis)
        self.verify_dealer(dealer)
        return self.seller_declarations()

    def to_review_ready(
        self,
        *,
        vehicle: tuple[str, str] | None = None,
        dealer: str = DEFAULT_DEALER,
    ) -> CaseView:
        self.to_preflight_passed(vehicle=vehicle, dealer=dealer)
        self.pair()
        self.join()
        return self.dealer_declarations()

    def to_both_confirmed(
        self,
        *,
        vehicle: tuple[str, str] | None = None,
        dealer: str = DEFAULT_DEALER,
    ) -> CaseView:
        self.to_review_ready(vehicle=vehicle, dealer=dealer)
        self.confirm(Actor.SELLER)
        return self.confirm(Actor.DEALER)


@pytest.fixture()
def journey(ctx: ServiceContext) -> Iterator[Journey]:
    yield Journey(ctx)


@pytest.fixture()
def api(settings: Settings):
    """A TestClient over the real app, with lifespan run.

    Used only by the contract and end-to-end HTTP tests. Invariant tests use
    ``journey`` instead, because an invariant that only holds over HTTP is not an
    invariant.
    """
    from fastapi.testclient import TestClient

    from app.main import create_app

    with TestClient(create_app(settings)) as client:
        yield client
