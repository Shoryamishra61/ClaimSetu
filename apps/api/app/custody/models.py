"""Typed wire models for the four-state custody-record API."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CustodyState(str, Enum):
    DRAFT = "DRAFT"
    INITIATED = "INITIATED"
    DEALER_SELECTED = "DEALER_SELECTED"
    CUSTODY_TRANSFERRED = "CUSTODY_TRANSFERRED"


class InitiateCaseRequest(StrictModel):
    vehicle_no: str = Field(min_length=4, max_length=32)
    chassis_suffix: str = Field(min_length=3, max_length=32)
    seller_id: str = Field(min_length=3, max_length=64)


class DealerLookupRequest(StrictModel):
    # Format errors, including excess length, are deliberately handled by the
    # domain service so every malformed GSTIN receives the promised HTTP 400.
    gstin: str | None = None
    trade_certificate_no: str | None = Field(default=None, min_length=3, max_length=64)


class StateTransitionRequest(StrictModel):
    state: CustodyState
    dealer_id: str | None = Field(default=None, min_length=3, max_length=64)
    odometer_reading: int | None = None
    seller_confirmed: bool = False
    dealer_confirmed: bool = False


__all__ = [
    "CustodyState",
    "DealerLookupRequest",
    "InitiateCaseRequest",
    "StateTransitionRequest",
    "StrictModel",
]
