"""Policy registry and selection guard.

The only way to obtain a policy definition at runtime is ``get()``. It enforces
two things that INV-10 and threat T12 depend on:

- the requested version must be in ``SELECTABLE``;
- the definition must have ``in_force=True``.

Draft policy is importable (so tests and the source drawer can describe it) but
never selectable. That is the difference between documenting a proposal and
executing it.
"""

from __future__ import annotations

from ..policy_types import PolicyDefinition
from .cmvr_901e_2022_current import CURRENT_POLICY

#: The version the product runs on. Asserted by tests so a config typo fails CI
#: rather than silently changing which law the prototype claims to represent.
CURRENT_POLICY_VERSION = CURRENT_POLICY.version

SELECTABLE: dict[str, PolicyDefinition] = {
    CURRENT_POLICY.version: CURRENT_POLICY,
}


class PolicyNotSelectable(Exception):
    """Raised when a caller asks for a policy that must not run."""


def get(version: str) -> PolicyDefinition:
    definition = SELECTABLE.get(version)
    if definition is None:
        raise PolicyNotSelectable(
            f"Policy version {version!r} is not selectable. "
            f"Selectable versions: {sorted(SELECTABLE)}"
        )
    if not definition.in_force:
        # Defence in depth: even if something were added to SELECTABLE by
        # mistake, a not-in-force definition still cannot run.
        raise PolicyNotSelectable(
            f"Policy version {version!r} is not in force and cannot be used."
        )
    return definition


def current() -> PolicyDefinition:
    return get(CURRENT_POLICY_VERSION)
