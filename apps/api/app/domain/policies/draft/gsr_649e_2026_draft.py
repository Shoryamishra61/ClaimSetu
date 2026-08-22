"""DRAFT_NOT_IN_FORCE -- G.S.R. 649(E), 21 Jul 2026.

This file exists so that the policy-watch is documented in code rather than in
someone's memory. It is **not** law and **must not** execute as law.

Status: G.S.R. 649(E) was published on 21 Jul 2026 as *draft rules for comment*
(source S11 in 14_SOURCE_LEDGER.md). It proposes, among other things, a Form 29CA
dealer-to-dealer intimation and additional dealer-possession preconditions.

Guards that keep it inert:

1. ``in_force=False``. ``PolicyService.get`` raises on any definition with
   ``in_force=False``, so it cannot be selected even by an explicit config value.
2. It is not registered in the selectable registry (``registry.SELECTABLE``).
3. ``tests/test_policy_draft_inert.py`` asserts both of the above, and asserts
   that the configured production policy version is the 2022 one.

If G.S.R. 649(E) -- or any successor -- is ever *finally notified*, the correct
procedure (per the RESEARCH RULE) is:

- re-read the official Gazette and confirm FINAL, not draft;
- record publication and effective dates;
- create a NEW policy version module with a new version string;
- add migration tests covering cases created under the old version;
- never mutate ``cmvr_901e_2022_current.py`` to mean something else.

The items below are intentionally left empty. Writing speculative evaluators for
draft text would create exactly the "improvised law" this project refuses to do.
The proposals are recorded prose-only, in ``PROPOSED_CHANGES``, for the source
drawer.
"""

from __future__ import annotations

# Three dots, not two: this module sits in ``app.domain.policies.draft``, so ``..``
# would resolve to ``app.domain.policies`` and there is no ``policy_types`` there.
from ...policy_types import PolicyDefinition

POLICY_VERSION = "GSR_649E_2026_DRAFT"

#: Prose-only record of what the draft proposes. Not evaluated, not enforced.
PROPOSED_CHANGES: tuple[str, ...] = (
    "A Form 29CA intimation for dealer-to-dealer movement of a registered vehicle.",
    "Additional conditions on when possession may be transferred to a dealer.",
    "A time-bound framework for how long a dealer may hold a registered vehicle.",
)

#: Allowed wording for any UI that mentions this, per 02_EVIDENCE_AND_CLAIMS_LEDGER.md
#: section E. Anything stronger than this is a banned claim.
ALLOWED_WORDING_EN = (
    "MoRTH has proposed additional 2026 rules; these are draft and are not "
    "executed by the prototype."
)
ALLOWED_WORDING_HI = (
    "MoRTH ने 2026 के अतिरिक्त नियम प्रस्तावित किए हैं; ये मसौदा हैं और यह प्रोटोटाइप "
    "इन्हें लागू नहीं करता।"
)

DRAFT_POLICY = PolicyDefinition(
    version=POLICY_VERSION,
    title="DRAFT ONLY -- G.S.R. 649(E), 21 Jul 2026, not in force",
    source_id="S11",
    source_locator="Draft rules published for comment",
    in_force=False,
    items=(),
)
