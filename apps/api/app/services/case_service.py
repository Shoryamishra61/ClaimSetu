"""Case lifecycle: creation, fixture selection, declarations.

Every public method here opens its own write transaction, authorises the caller,
guards the state, writes facts, and hands off to ``projection.refresh`` to work out
what those facts mean. None of them decides a state directly.
"""

from __future__ import annotations

import hashlib
import secrets
import sqlite3
from dataclasses import dataclass

from ..adapters.mock_dealer_registry import DealerRecord, DealerStatus, LookupPurpose
from ..clock import IST, new_id, utc_now
from ..db import repository as repo
from ..domain.policy_types import ResponsibleActor
from ..domain.states import (
    MUTABLE_STATES,
    SUPPORTED_JOURNEY_TYPES,
    Actor,
    CaseState,
    JourneyType,
)
from ..errors import AppError
from .context import ServiceContext
from .projection import CaseView, load_view, refresh

#: Bytes of entropy per party token. Same reasoning as pair codes: it is a bearer
#: credential for the duration of the demo, so it gets full-strength randomness.
PARTY_TOKEN_BYTES = 32


def hash_token(token: str) -> str:
    """SHA-256 of a bearer token.

    Plain SHA-256 rather than a password KDF on purpose: these are 256-bit random
    strings, not human-chosen secrets, so there is no dictionary to slow down. What
    matters is that the database never stores a usable credential.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def issue_party_token(
    connection: sqlite3.Connection,
    *,
    case_id: str,
    actor: Actor,
    session_id: str | None = None,
) -> str:
    token = secrets.token_urlsafe(PARTY_TOKEN_BYTES)
    repo.insert_party_session(
        connection,
        session_id=session_id or new_id(),
        case_id=case_id,
        actor=actor.value,
        token_hash=hash_token(token),
    )
    return token


@dataclass(frozen=True, slots=True)
class CreatedCase:
    view: CaseView
    #: Returned exactly once, at creation. Never stored in plaintext and never
    #: included in a case snapshot.
    seller_token: str


def load_case(connection: sqlite3.Connection, case_id: str) -> repo.CaseRow:
    case_row = repo.get_case(connection, case_id)
    if case_row is None:
        raise AppError("CASE_NOT_FOUND")
    return case_row


def authorise_actor(
    connection: sqlite3.Connection,
    *,
    case_id: str,
    token: str | None,
    required: Actor | None = None,
) -> Actor:
    """Resolve a bearer token to the party it authorises for this case.

    This is not identity verification and is not presented as such: it proves only
    that the caller is the device that created the case, or the device that
    redeemed the pairing code. That is exactly enough to stop one party acting as
    the other, which is the invariant that matters.
    """
    if not token:
        raise AppError("UNAUTHORISED_ACTOR")
    actor_value = repo.find_party_session(
        connection, case_id=case_id, token_hash=hash_token(token)
    )
    if actor_value is None:
        raise AppError("UNAUTHORISED_ACTOR")
    actor = Actor(actor_value)
    if required is not None and actor is not required:
        raise AppError("UNAUTHORISED_ACTOR", detail={"required": required.value})
    return actor


def require_mutable(case_row: repo.CaseRow) -> None:
    if case_row.current_state is CaseState.HANDOFF_ACKNOWLEDGED:
        raise AppError("ALREADY_ACKNOWLEDGED")
    if case_row.current_state not in MUTABLE_STATES:
        raise AppError("INVALID_STATE", detail={"state": case_row.current_state.value})


class CaseService:
    def __init__(self, ctx: ServiceContext) -> None:
        self.ctx = ctx

    # -- commands --------------------------------------------------------------

    def create_case(self, *, journey_type: str) -> CreatedCase:
        """Start a case, or refuse the unsupported route.

        INV-08 is enforced by refusing to create a row at all. A private-buyer
        case does not exist in a "wrong journey" state that later code has to
        remember to check -- there is nothing to check.
        """
        try:
            journey = JourneyType(journey_type)
        except ValueError:
            raise AppError(
                "VALIDATION_ERROR", detail={"field": "journey_type"}
            ) from None
        if journey not in SUPPORTED_JOURNEY_TYPES:
            raise AppError("UNSUPPORTED_JOURNEY", detail={"journey_type": journey.value})

        case_id = new_id()
        with self.ctx.db.write() as connection:
            case_row = repo.insert_case(
                connection,
                case_id=case_id,
                journey_type=journey.value,
                policy_version=self.ctx.policy.version,
                state=CaseState.DRAFT,
            )
            # Fixed once, at creation. If this were recomputed on every read the
            # canonical hash would move continuously and no confirmation could
            # ever survive long enough to be used.
            repo.update_case(
                connection,
                case_id,
                handover_local_time=utc_now().astimezone(IST).isoformat(
                    timespec="seconds"
                ),
            )
            token = issue_party_token(connection, case_id=case_id, actor=Actor.SELLER)
            repo.append_event(
                connection,
                case_id=case_id,
                event_type="CASE_CREATED",
                actor=Actor.SELLER.value,
                state_after=CaseState.DRAFT,
                detail={"journey_type": journey.value},
            )
            case_row = load_case(connection, case_id)
            view = load_view(self.ctx, connection, case_row)
        return CreatedCase(view=view, seller_token=token)

    def verify_vehicle(
        self, *, case_id: str, token: str | None, registration_no: str, chassis_suffix: str
    ) -> CaseView:
        with self.ctx.db.write() as connection:
            case_row = load_case(connection, case_id)
            authorise_actor(
                connection, case_id=case_id, token=token, required=Actor.SELLER
            )
            require_mutable(case_row)
            record = self.ctx.vehicles.lookup(
                registration_no=registration_no, chassis_suffix=chassis_suffix
            )
            if record is None:
                raise AppError("VEHICLE_NOT_FOUND")
            repo.update_case(connection, case_id, vehicle_id=record.id)
            case_row = load_case(connection, case_id)
            return refresh(
                self.ctx,
                connection,
                case_row,
                actor=Actor.SELLER,
                event_type="VEHICLE_VERIFIED",
                detail={"vehicle_id": record.id, "simulated": True},
            )

    def verify_dealer(
        self, *, case_id: str, token: str | None, authorisation_no: str
    ) -> CaseView:
        """Record which dealer, and what the simulated registry says about them.

        A dealer whose authorisation is EXPIRED or SUSPENDED is still recorded, so
        the case lands in DEALER_INVALID and the UI can explain why with the actual
        status. Only a number the registry has never heard of is an error, because
        there is nothing to record.
        """
        with self.ctx.db.write() as connection:
            case_row = load_case(connection, case_id)
            authorise_actor(
                connection, case_id=case_id, token=token, required=Actor.SELLER
            )
            require_mutable(case_row)
            if case_row.vehicle_id is None:
                raise AppError(
                    "INVALID_STATE", detail={"state": case_row.current_state.value}
                )
            result = self.ctx.dealers.lookup(
                authorisation_no=authorisation_no, purpose=LookupPurpose.VERIFICATION
            )
            if not isinstance(result, DealerRecord):
                raise AppError("DEALER_NOT_FOUND")
            repo.update_case(
                connection,
                case_id,
                dealer_id=result.authorisation_no,
                dealer_status_at_verify=result.status.value,
            )
            case_row = load_case(connection, case_id)
            return refresh(
                self.ctx,
                connection,
                case_row,
                actor=Actor.SELLER,
                event_type="DEALER_VERIFIED",
                detail={
                    "authorisation_no": result.authorisation_no,
                    "status": result.status.value,
                    "simulated": True,
                },
            )

    def set_declarations(
        self, *, case_id: str, token: str | None, values: dict[str, bool]
    ) -> CaseView:
        """Record declarations, enforcing who is allowed to make which.

        The per-code actor check is load-bearing: without it a seller could tick
        the dealer's possession confirmation, and the app would be asserting that
        the dealer said something the dealer never said.
        """
        with self.ctx.db.write() as connection:
            case_row = load_case(connection, case_id)
            actor = authorise_actor(connection, case_id=case_id, token=token)
            require_mutable(case_row)

            settable = self.ctx.policy.declaration_codes()
            unknown = sorted(set(values) - settable)
            if unknown:
                raise AppError("VALIDATION_ERROR", detail={"unknown_codes": unknown})

            source_types: dict[str, str] = {}
            not_yours: list[str] = []
            for code in values:
                item = self.ctx.policy.item(code)
                assert item is not None  # guaranteed by the settable check above
                source_types[code] = item.source_type.value
                if (item.responsible is ResponsibleActor.SELLER and actor is not Actor.SELLER) or (item.responsible is ResponsibleActor.DEALER and actor is not Actor.DEALER):
                    not_yours.append(code)
            if not_yours:
                raise AppError(
                    "UNAUTHORISED_ACTOR", detail={"codes": sorted(not_yours)}
                )

            if values:
                repo.upsert_declarations(
                    connection,
                    case_id,
                    values=values,
                    source_types=source_types,
                    policy_version=self.ctx.policy.version,
                    actor=actor.value,
                )
            case_row = load_case(connection, case_id)
            return refresh(
                self.ctx,
                connection,
                case_row,
                actor=actor,
                event_type="DECLARATIONS_UPDATED",
                detail={"codes": sorted(values)},
            )

    def cancel(self, *, case_id: str, token: str | None) -> CaseView:
        with self.ctx.db.write() as connection:
            case_row = load_case(connection, case_id)
            authorise_actor(
                connection, case_id=case_id, token=token, required=Actor.SELLER
            )
            if case_row.current_state is CaseState.CANCELLED:
                return load_view(self.ctx, connection, case_row)
            if case_row.current_state is CaseState.HANDOFF_ACKNOWLEDGED:
                raise AppError("ALREADY_ACKNOWLEDGED")
            # SUBMITTING_29C has no edge to CANCELLED: a request is in flight and
            # its outcome must be recorded rather than discarded.
            if case_row.current_state is CaseState.SUBMITTING_29C:
                raise AppError("SUBMISSION_IN_PROGRESS")
            state_before = case_row.current_state
            repo.transition_state(
                connection,
                case_id,
                expected=(state_before,),
                new_state=CaseState.CANCELLED,
            )
            repo.invalidate_pair_sessions(connection, case_id)
            repo.append_event(
                connection,
                case_id=case_id,
                event_type="CASE_CANCELLED",
                actor=Actor.SELLER.value,
                state_before=state_before,
                state_after=CaseState.CANCELLED,
            )
            case_row = load_case(connection, case_id)
            return load_view(self.ctx, connection, case_row)

    # -- queries ---------------------------------------------------------------

    def snapshot(self, *, case_id: str) -> CaseView:
        with self.ctx.db.read() as connection:
            case_row = load_case(connection, case_id)
            return load_view(self.ctx, connection, case_row)

    def actor_for(self, *, case_id: str, token: str | None) -> Actor | None:
        """Best-effort actor resolution for read endpoints.

        Returns None instead of raising: a case snapshot is not secret (it contains
        only fictional data and no tokens), so an unrecognised device can still see
        the state. It simply cannot act.
        """
        if not token:
            return None
        with self.ctx.db.read() as connection:
            actor_value = repo.find_party_session(
                connection, case_id=case_id, token_hash=hash_token(token)
            )
        return Actor(actor_value) if actor_value is not None else None

    def audit_trail(self, *, case_id: str) -> list[repo.AuditEventRow]:
        with self.ctx.db.read() as connection:
            load_case(connection, case_id)
            return repo.list_events(connection, case_id)

    def dealer_revalidation(self, *, case_id: str) -> DealerRecord | None:
        with self.ctx.db.read() as connection:
            case_row = load_case(connection, case_id)
        if case_row.dealer_id is None:
            return None
        result = self.ctx.dealers.lookup(
            authorisation_no=case_row.dealer_id, purpose=LookupPurpose.REVALIDATION
        )
        return result if isinstance(result, DealerRecord) else None


__all__ = [
    "CaseService",
    "CreatedCase",
    "DealerStatus",
    "authorise_actor",
    "hash_token",
    "issue_party_token",
    "load_case",
    "require_mutable",
]
