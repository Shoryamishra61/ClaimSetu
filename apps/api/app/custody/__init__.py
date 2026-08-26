"""Four-state custody-record compatibility slice from handover29c-master-spec.md.

This namespace intentionally remains separate from the acknowledgement-gated Form 29C
workflow. A generated PDF is a pre-filled prototype record; it is not a government
submission, statutory e-signature, or acknowledgement.
"""

from .schema import initialise_custody_schema

__all__ = ["initialise_custody_schema"]
