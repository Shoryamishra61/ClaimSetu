"""Request bodies.

Pydantic is used for *input* only. Responses are built by the hand-written
allow-list serialisers in ``serialisers.py``, because the security property that
matters on the way out is "no secret ever appears", and an explicit allow-list
fails closed where a mirrored model would drift.

The validators here are narrow on purpose. They enforce shape and length -- enough
to keep obviously malformed input out of the services -- and nothing else. Business
validation stays in the services so the invariant tests cover it.

One thing this file deliberately does NOT do: accept any field that could carry
personal data. No request model has a name, address, phone, Aadhaar, PAN, OTP,
password or payment field, because the product has no use for one -- it moves a
vehicle between a registered owner and an authorised dealer, and the only identity
it needs is possession of a party token.

The one name the product ever displays, ``registered_owner_name``, is *output*
only: it comes from the fictional vehicle fixture, where every value is suffixed
``(fictional)``, and no route accepts it. Both halves -- what is refused on the way
in, and where the single name comes from -- are asserted by
``tests/test_no_sensitive_fields.py``.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    """Rejects unknown keys.

    ``extra="forbid"`` means a client that invents a field gets a 422 rather than
    having it silently ignored -- which is how a "just add a flag" workaround gets
    written against an API that appeared to accept it.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CreateCaseRequest(StrictModel):
    journey_type: str = Field(min_length=1, max_length=64)


class VehicleVerifyRequest(StrictModel):
    #: Fictional demo plate. Length caps are generous enough for any real Indian
    #: format plus separators, because rejecting a plausible plate would look like
    #: a bug during a demo.
    registration_no: str = Field(min_length=4, max_length=32)
    chassis_suffix: str = Field(min_length=3, max_length=32)


class DealerVerifyRequest(StrictModel):
    #: The dealer's Form 29B authorisation number. A business registration
    #: identifier, not a personal one: it names a licensed dealership in the
    #: simulated registry and says nothing about any individual.
    authorisation_no: str = Field(min_length=3, max_length=64)


class DeclarationsRequest(StrictModel):
    #: Declaration code -> value. Which codes exist, and which actor may set each
    #: one, is decided by the policy definition, not here.
    values: dict[str, bool] = Field(default_factory=dict, max_length=64)

    @field_validator("values")
    @classmethod
    def _codes_look_like_codes(cls, value: dict[str, bool]) -> dict[str, bool]:
        for code in value:
            if not code or len(code) > 64:
                raise ValueError("declaration codes must be 1-64 characters")
        return value


class JoinPairRequest(StrictModel):
    #: The seller's one-time code. Upper bound is well above the 43-character
    #: base64url encoding of 32 bytes, so a longer future token still fits.
    code: str = Field(min_length=8, max_length=256)


class ConfirmRequest(StrictModel):
    #: Hex SHA-256 of the payload the confirming party was shown. Exactly 64 hex
    #: characters -- a client sending anything else has a bug, and saying so at the
    #: boundary is clearer than a STALE_PAYLOAD further in.
    payload_hash: str = Field(min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")


class SubmitRequest(StrictModel):
    payload_hash: str = Field(min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")


__all__ = [
    "ConfirmRequest",
    "CreateCaseRequest",
    "DealerVerifyRequest",
    "DeclarationsRequest",
    "JoinPairRequest",
    "StrictModel",
    "SubmitRequest",
    "VehicleVerifyRequest",
]
