"""Runtime copy lint: what this prototype may and may not say.

02_EVIDENCE_AND_CLAIMS_LEDGER.md is the source of truth for claims. Several earlier
concepts were rejected outright ("Risk Shield", a Section 65B certificate, a
Section 148 registered-bailee framing, Jaro-Winkler name matching, GPS proof of
co-presence). A rejected claim must not come back through a comment, a leftover
identifier, or a screen that nobody re-read.

**What this file scans, and why that scope.** Only *string literals* in the source
tree, with docstrings excluded. A string literal is the only thing that can reach a
user's screen; a docstring is documentation. That distinction matters here: the
codebase deliberately *discusses* rejected concepts in prose (this module's own
docstring does), and a lint that could not tell the difference would force the
documentation to stop naming what it rejected.

**Two escape hatches, both narrow.** ``DENIAL_ONLY_TERMS`` covers words the product
is *required* to name while refusing them -- "do not enter real Aadhaar, PAN, OTP",
"it is not an electronic signature". Banning those words outright would ban the
warning. ``ALLOWED_LITERALS`` covers the one string that matches a ban while doing
the opposite of it: the Permissions-Policy header names ``geolocation`` in order to
switch it off.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest

from app import copy as copy_module
from app.config import REPO_ROOT
from app.errors import ERROR_CATALOGUE

API_SOURCE_ROOT = REPO_ROOT / "apps" / "api" / "app"
WEB_SOURCE_ROOT = REPO_ROOT / "apps" / "web" / "src"
FIXTURE_ROOT = REPO_ROOT / "fixtures"


#: Claims the ledger rejects. Matched case-insensitively against user-visible text.
#:
#: Each entry carries the reason, because a future contributor hitting this lint
#: needs to know it is a specification decision and not a style preference.
BANNED_CLAIMS: dict[str, str] = {
    r"risk\s*shield": "The TitleTransfer Risk Shield concept was discarded (01, memo).",
    r"liability\s+(is\s+)?severed": "Ledger: liability severance is not a claim this product may make.",
    r"fully\s+protected": "Ledger: no protection claim of any kind.",
    r"section\s*65\s*b": "Ledger: no Section 65B certificate. Rejected claim.",
    r"registered\s+bailee": "Ledger: the Section 148 bailee framing was rejected.",
    r"jaro[-\s]?winkler": "Ledger: no name-similarity threshold is presented as regulatory.",
    r"government\s+verified": "Nothing here is verified by a government. Simulated only.",
    r"official\s+acknowledgement": "The acknowledgement is simulated; 'official' is forbidden.",
    r"legally\s+(valid|binding|effective)": "Nothing produced here has legal effect.",
    r"court[-\s]?certified": "Rejected claim.",
    r"criminal\s+liability\s+transfer": "Rejected claim.",
    r"\.gov\.in": "No government domain identity, real or fake.",
    r"\.nic\.in": "No government domain identity, real or fake.",
    r"titletransfer": "Name of the discarded concept.",
    r"\bvahan\b": "No live VAHAN integration exists, so the name must not appear as a source.",
    r"api\s*setu\b": "No live API Setu integration exists.",
    r"\bgps\b": "No geolocation is collected or claimed.",
    r"geolocation": "No geolocation is collected or claimed.",
    r"\b50\s*m\b": "The 50-metre co-presence proof was rejected.",
    r"proof\s+of\s+co-?presence": "Rejected claim.",
    # Narrow on purpose. Bare "liveness" is ordinary operations vocabulary (a
    # liveness probe); what the ledger rejects is the biometric feature.
    r"(face|facial|selfie)[\s-]*(liveness|recognition|match|scan|verification)":
        "Facial recognition and liveness were not built and must not be implied.",
    r"liveness\s+(detection|capture)": "Rejected feature.",
}

#: String literals that match a banned pattern but are the *opposite* of the claim.
#:
#: One entry only, and it earns its place: the Permissions-Policy header names
#: ``geolocation`` in order to switch it off. A lint that forced this to be renamed
#: or suppressed would be trading a real security control for a text match.
ALLOWED_LITERALS: frozenset[str] = frozenset(
    {"geolocation=(), camera=(), microphone=(), payment=(), usb=()"}
)

#: Terms the product must be able to name, but only inside a denial.
#:
#: Three of these (Aadhaar, PAN, OTP) appear because the product is *required* to
#: say it does not accept them; banning the words outright would ban the warning.
#: The signature terms are here for the same reason: the confirmation copy has to
#: say it is *not* an electronic signature.
DENIAL_ONLY_TERMS: dict[str, str] = {
    r"\baadhaar\b": "may only appear in a 'do not enter real ...' warning",
    r"\bpan\b": "may only appear in a 'do not enter real ...' warning",
    r"\botp\b": "may only appear in a 'do not enter real ...' warning",
    r"\be-?sign\w*": "may only appear while denying that anything here is an eSign",
    r"digital\s+signature\s+certificate": "may only appear while denying a DSC is used",
}

#: A string carrying a denial-only term must also carry one of these. Both languages,
#: because the Hindi copy carries exactly the same duty as the English.
DENIAL_MARKERS = (
    "do not enter",
    "does not accept",
    "neither needs nor accepts",
    "no name, address",
    "there is no",
    "is not an",
    "is not a ",
    "does not",
    "न करें",
    "स्वीकार नहीं",
    "नहीं है",
    "नहीं करता",
)


def user_visible_strings(path: Path) -> list[tuple[int, str]]:
    """Every string literal in a Python file except docstrings.

    Docstrings are located by asking the AST for them rather than by guessing from
    position, so a module whose first statement is a real string expression is not
    mistaken for documentation.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    docstring_nodes: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            body = getattr(node, "body", None)
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                docstring_nodes.add(id(body[0].value))

    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and id(node) not in docstring_nodes
        ):
            found.append((node.lineno, node.value))
    return found


def python_sources(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)


def banned_patterns_in(text: str) -> list[str]:
    """Every banned pattern the text matches, unless the text is allowlisted.

    Returns descriptions rather than booleans so a failure names the pattern and
    the reason, which is the difference between a lint a contributor can act on and
    one they work around.
    """
    if any(allowed in text for allowed in ALLOWED_LITERALS):
        return []
    lowered = text.lower()
    return [
        f"/{pattern}/ -- {reason}"
        for pattern, reason in BANNED_CLAIMS.items()
        if re.search(pattern, lowered)
    ]


def denial_only_terms_without_a_denial(text: str) -> list[str]:
    """Denial-only terms present in a string that does not read as a denial."""
    lowered = text.lower()
    hits = [
        f"/{pattern}/ -- {note}"
        for pattern, note in DENIAL_ONLY_TERMS.items()
        if re.search(pattern, lowered)
    ]
    if not hits:
        return []
    if any(marker in lowered for marker in DENIAL_MARKERS):
        return []
    return hits


API_FILES = python_sources(API_SOURCE_ROOT)


def test_the_lint_actually_has_something_to_scan() -> None:
    """A lint over an empty file list is worse than no lint: it reports green.

    If a refactor moves the app, this fails rather than quietly passing.
    """
    assert len(API_FILES) >= 20, f"only found {len(API_FILES)} API source files"


@pytest.mark.invariant
@pytest.mark.parametrize("path", API_FILES, ids=lambda p: p.name)
def test_no_banned_claim_in_api_string_literals(path: Path) -> None:
    offences = [
        f"{path.name}:{lineno} matched {hit}"
        for lineno, text in user_visible_strings(path)
        for hit in banned_patterns_in(text)
    ]
    assert offences == [], "\n".join(offences)


@pytest.mark.invariant
def test_denial_only_terms_appear_only_inside_a_denial() -> None:
    """Aadhaar/PAN/OTP/eSign may be named, but only to say they are not used."""
    offences = [
        f"{path.name}:{lineno} {hit} in {text[:70]!r}"
        for path in API_FILES
        for lineno, text in user_visible_strings(path)
        for hit in denial_only_terms_without_a_denial(text)
    ]
    assert offences == [], "\n".join(offences)


@pytest.mark.invariant
def test_the_required_no_real_data_warning_is_the_one_that_names_them() -> None:
    """Guards the previous test against passing because nothing mentions them.

    The warning is a requirement in its own right: the product must state, at the
    point of input, which data it will not take.
    """
    lowered = copy_module.NO_REAL_DATA_EN.lower()
    for term in ("aadhaar", "pan", "otp", "password", "payment"):
        assert term in lowered, f"NO_REAL_DATA_EN does not name {term}"
    assert denial_only_terms_without_a_denial(copy_module.NO_REAL_DATA_EN) == []
    assert denial_only_terms_without_a_denial(copy_module.NO_REAL_DATA_HI) == []


@pytest.mark.invariant
def test_no_banned_claim_in_error_messages() -> None:
    """Error copy is user-visible copy, and it is where over-claiming creeps in.

    Checked against the catalogue rather than the file, so a message assembled at
    import time is covered too.
    """
    offences = [
        f"{code}.{language} matched {hit}"
        for code, spec in ERROR_CATALOGUE.items()
        for language, message in (("en", spec.message_en), ("hi", spec.message_hi))
        for hit in banned_patterns_in(message)
    ]
    assert offences == [], "\n".join(offences)


@pytest.mark.invariant
def test_error_messages_never_claim_a_government_system_answered() -> None:
    """Where a simulated source is involved, the message must name it as simulated."""
    for code, spec in ERROR_CATALOGUE.items():
        lowered = spec.message_en.lower()
        if "registry" in lowered or "acknowledge" in lowered:
            assert "simulat" in lowered or "prototype" in lowered or "demo" in lowered, (
                f"{code} mentions a registry or acknowledgement without saying it is "
                f"simulated: {spec.message_en!r}"
            )


@pytest.mark.invariant
def test_every_error_has_bilingual_copy() -> None:
    """Error copy is critical copy, so it is in scope for the language requirement."""
    for code, spec in ERROR_CATALOGUE.items():
        assert spec.message_en.strip(), code
        assert spec.message_hi.strip(), code
        # Devanagari present, i.e. the Hindi field is not an English placeholder.
        assert re.search(r"[ऀ-ॿ]", spec.message_hi), (
            f"{code} has no Devanagari in message_hi"
        )


# ---------------------------------------------------------------------------
# The disclosure the product is required to carry
# ---------------------------------------------------------------------------

#: Verbatim from the brief and 05_UX_UI_INTERACTION_SPEC.md section 3. Pinned as a
#: literal here so a reword in app/copy.py is a failing test rather than a silent
#: weakening of the disclosure.
REQUIRED_DISCLOSURE_EN = (
    "Independent hackathon prototype · Government integrations are simulated · "
    "Uses fictional data"
)


@pytest.mark.invariant
def test_disclosure_wording_is_exact() -> None:
    assert copy_module.DISCLOSURE_EN == REQUIRED_DISCLOSURE_EN


@pytest.mark.invariant
def test_disclosure_states_all_three_facts() -> None:
    """Asserted separately from the exact string so the *reason* survives a reword.

    If the wording ever legitimately changes, this test says which facts the new
    wording still has to carry.
    """
    lowered = copy_module.DISCLOSURE_EN.lower()
    assert "independent hackathon prototype" in lowered
    assert "simulated" in lowered
    assert "fictional" in lowered


@pytest.mark.invariant
def test_required_copy_is_bilingual() -> None:
    pairs = (
        ("DISCLOSURE", copy_module.DISCLOSURE_EN, copy_module.DISCLOSURE_HI),
        ("ABOUT", copy_module.ABOUT_EN, copy_module.ABOUT_HI),
        ("NO_REAL_DATA", copy_module.NO_REAL_DATA_EN, copy_module.NO_REAL_DATA_HI),
        ("SCOPE", copy_module.SCOPE_EN, copy_module.SCOPE_HI),
        (
            "CONFIRMATION_MEANING",
            copy_module.CONFIRMATION_MEANING_EN,
            copy_module.CONFIRMATION_MEANING_HI,
        ),
        (
            "ACKNOWLEDGEMENT_CAVEAT",
            copy_module.ACKNOWLEDGEMENT_CAVEAT_EN,
            copy_module.ACKNOWLEDGEMENT_CAVEAT_HI,
        ),
        ("POLICY_ANCHOR", copy_module.POLICY_ANCHOR_EN, copy_module.POLICY_ANCHOR_HI),
    )
    for name, english, hindi in pairs:
        assert english.strip(), name
        assert hindi.strip(), name
        assert re.search(r"[ऀ-ॿ]", hindi), f"{name}_HI has no Devanagari"


@pytest.mark.invariant
def test_about_copy_makes_the_four_required_denials() -> None:
    lowered = copy_module.ABOUT_EN.lower()
    assert "independent hackathon prototype" in lowered
    assert "does not connect to any government system" in lowered
    assert "legal effect" in lowered
    assert "fictional" in lowered


@pytest.mark.invariant
def test_confirmation_copy_denies_being_a_signature() -> None:
    """Confirmation is not submission, and it is not a signature. Said on-screen."""
    lowered = copy_module.CONFIRMATION_MEANING_EN.lower()
    assert "not an electronic signature" in lowered
    assert "does not submit anything" in lowered


@pytest.mark.invariant
def test_acknowledgement_caveat_says_the_number_is_fictional() -> None:
    lowered = copy_module.ACKNOWLEDGEMENT_CAVEAT_EN.lower()
    assert "simulated" in lowered
    assert "fictional" in lowered
    assert "not proof" in lowered


@pytest.mark.invariant
def test_scope_copy_names_the_excluded_route() -> None:
    """A user on the wrong journey is told the other process exists elsewhere."""
    lowered = copy_module.SCOPE_EN.lower()
    assert "authorised dealer" in lowered
    assert "private buyer" in lowered
    assert "out of scope" in lowered


@pytest.mark.invariant
def test_policy_anchor_names_the_in_force_instrument_only() -> None:
    """The anchor is the 2022 instrument. The 2026 draft must not appear here."""
    text = copy_module.POLICY_ANCHOR_EN
    assert "901(E)" in text
    assert "1 April 2023" in text
    assert "649" not in text
    assert "29CA" not in text


@pytest.mark.invariant
def test_meta_payload_carries_the_disclosure_and_the_simulation_flag() -> None:
    """The SPA renders this verbatim, so the wording is covered on every screen."""
    payload = copy_module.meta_payload(
        build_label="test", policy_version="CMVR_901E_2022_CURRENT",
        poll_interval_seconds=2.0,
    )
    assert payload["simulation"] is True
    assert payload["disclosure"] == {
        "en": copy_module.DISCLOSURE_EN,
        "hi": copy_module.DISCLOSURE_HI,
    }
    for key in ("about", "no_real_data", "scope", "confirmation_meaning",
                "acknowledgement_caveat", "policy_anchor"):
        assert set(payload[key]) == {"en", "hi"}, key


# ---------------------------------------------------------------------------
# Fixtures must be visibly fictional
# ---------------------------------------------------------------------------


@pytest.mark.invariant
def test_fixture_data_is_visibly_fictional() -> None:
    """Every demo registration starts DEMO.

    Not cosmetic: a plausible-looking real registration number in a demo is how a
    reviewer ends up unsure whether they are looking at live data.
    """
    vehicles = json.loads((FIXTURE_ROOT / "vehicles.json").read_text(encoding="utf-8"))
    for record in vehicles["vehicles"]:
        assert record["registration_no"].startswith("DEMO"), record["registration_no"]

    dealers = json.loads((FIXTURE_ROOT / "dealers.json").read_text(encoding="utf-8"))
    for record in dealers["dealers"]:
        assert record["authorisation_no"].startswith("DEMO-"), record["authorisation_no"]


@pytest.mark.invariant
def test_fixtures_contain_no_banned_claim() -> None:
    offences = [
        f"{path.name}:{lineno} matched {hit}"
        for path in sorted(FIXTURE_ROOT.glob("*.json"))
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        )
        for hit in banned_patterns_in(line)
    ]
    assert offences == [], "\n".join(offences)


# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------


@pytest.mark.invariant
def test_frontend_sources_contain_no_banned_claim() -> None:
    """Scans the SPA once it exists.

    Deliberately not skipped when the directory is missing: a skip reads as green,
    and the acceptance gate for runtime copy is not satisfiable until this scan has
    actually run over the shipped frontend. BUILD_STATUS.md tracks that separately.

    Scanned line by line rather than whole-file so ``ALLOWED_LITERALS`` still
    applies -- the frontend is also entitled to name ``geolocation`` in order to
    switch it off.
    """
    assert WEB_SOURCE_ROOT.is_dir(), (
        f"{WEB_SOURCE_ROOT} does not exist yet, so the runtime-copy gate for the "
        "frontend is unproven. This test is expected to fail until the SPA is built."
    )
    patterns = ("*.ts", "*.tsx", "*.html", "*.css", "*.json")
    files = sorted(
        p
        for pattern in patterns
        for p in WEB_SOURCE_ROOT.rglob(pattern)
        if "node_modules" not in p.parts
    )
    assert files, "frontend source directory exists but contains nothing to scan"

    offences = [
        f"{path.name}:{lineno} matched {hit}"
        for path in files
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
        )
        for hit in banned_patterns_in(line)
    ]
    assert offences == [], "\n".join(offences)


@pytest.mark.invariant
def test_frontend_carries_the_disclosure_verbatim() -> None:
    """The banner must exist in the shipped bundle, not only in the API response.

    Checked as a substring of the whole frontend tree because the component that
    renders it may compose it from the ``/meta`` payload; either way the required
    wording, or the fetch that supplies it, has to be present.
    """
    assert WEB_SOURCE_ROOT.is_dir(), (
        f"{WEB_SOURCE_ROOT} does not exist yet. Expected to fail until the SPA is "
        "built."
    )
    combined = "\n".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in WEB_SOURCE_ROOT.rglob("*")
        if p.is_file() and p.suffix in {".ts", ".tsx", ".html"}
    )
    assert "disclosure" in combined.lower(), (
        "no frontend source references the disclosure copy"
    )
