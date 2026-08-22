"""The interpreter baseline, asserted rather than assumed.

``requirements.txt`` says: "Target interpreter: CPython 3.10 ... Nothing in this
codebase uses a 3.11+ construct -- asserted by tests/test_python_baseline.py, not by
good intentions." This is that file.

Why it exists at all. The brief's technical default was Python 3.12; the interpreter
actually available on the build machine is 3.10.11, and ADR-007 records the decision
to keep it rather than install a second runtime two days before a deadline. That
decision is only safe if something enforces it, because 3.11+ constructs are easy to
reach for and most of them fail at *runtime*, on one branch, rather than at import.
``StrEnum`` and ``datetime.UTC`` are the two that would most plausibly slip in.

**How the check works, and what it cannot prove.** Two independent passes:

1.  ``ast.parse(..., feature_version=(3, 10))`` over every module. This catches
    *grammar* that postdates 3.10 -- ``except*``, PEP 695 ``type`` statements --
    regardless of which interpreter runs the suite. It is documented as best-effort,
    and it cannot parse *above* the running interpreter's version, so on 3.10 it is
    largely a no-op that becomes load-bearing if the suite ever runs on 3.12.
2.  A name scan for 3.11+ standard-library additions. This is what catches the
    realistic mistake: valid syntax on every version, absent attribute on 3.10.

Neither pass can prove a *behavioural* difference is unhit -- 3.11 relaxed
``datetime.fromisoformat``, and code that parses a ``Z``-suffixed timestamp is valid
and working on 3.11 while raising ``ValueError`` on 3.10. That specific case is
covered explicitly at the end of this file, because this codebase does parse stored
timestamps.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

from app import clock
from app.config import REPO_ROOT

API_ROOT = REPO_ROOT / "apps" / "api"
APP_ROOT = API_ROOT / "app"

#: The interpreter this build targets. Written here as data so the two places that
#: also state it -- requirements.txt prose and ruff's target-version -- can be
#: checked against one value instead of against each other's wording.
TARGET_VERSION = (3, 10)


def source_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)


APP_FILES = source_files(APP_ROOT)
TEST_FILES = source_files(API_ROOT / "tests")


# ---------------------------------------------------------------------------
# pass 1: grammar
# ---------------------------------------------------------------------------


def test_there_are_files_to_check() -> None:
    assert len(APP_FILES) >= 20, f"only found {len(APP_FILES)} modules under {APP_ROOT}"


@pytest.mark.parametrize("path", APP_FILES, ids=lambda p: p.name)
def test_module_parses_under_the_target_grammar(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    try:
        ast.parse(source, filename=str(path), feature_version=TARGET_VERSION)
    except SyntaxError as exc:  # pragma: no cover - the failure is the point
        pytest.fail(
            f"{path.name} does not parse as Python "
            f"{TARGET_VERSION[0]}.{TARGET_VERSION[1]}: line {exc.lineno}: {exc.msg}"
        )


@pytest.mark.parametrize("path", TEST_FILES, ids=lambda p: p.name)
def test_test_module_parses_under_the_target_grammar(path: Path) -> None:
    """The suite itself has to run on the target interpreter too.

    A test file using 3.11 syntax fails at collection, which reads as "the tests are
    broken" rather than "the baseline was violated".
    """
    source = path.read_text(encoding="utf-8")
    try:
        ast.parse(source, filename=str(path), feature_version=TARGET_VERSION)
    except SyntaxError as exc:  # pragma: no cover
        pytest.fail(f"{path.name}: line {exc.lineno}: {exc.msg}")


# ---------------------------------------------------------------------------
# pass 2: names that do not exist on 3.10
# ---------------------------------------------------------------------------

#: Names reachable only through an import. Checked on ``import`` / ``from ... import``
#: rather than on every ``Name`` node, because that is the only way a stdlib addition
#: can enter a module -- and checking Name nodes would flag a local called ``override``.
FORBIDDEN_IMPORTED_NAMES: dict[str, str] = {
    "tomllib": "3.11 stdlib module; parse TOML with a regex or add a dependency",
    "StrEnum": "3.11 (enum); use `class X(str, Enum)`",
    "ReprEnum": "3.11 (enum)",
    "EnumCheck": "3.11 (enum)",
    "Self": "3.11 (typing); annotate the class by name under `from __future__`",
    "Never": "3.11 (typing); use NoReturn",
    "LiteralString": "3.11 (typing)",
    "assert_never": "3.11 (typing)",
    "assert_type": "3.11 (typing)",
    "reveal_type": "3.11 (typing)",
    "dataclass_transform": "3.11 (typing)",
    "TypeVarTuple": "3.11 (typing)",
    "Unpack": "3.11 (typing)",
    "TaskGroup": "3.11 (asyncio); gather() covers this codebase's needs",
    "file_digest": "3.11 (hashlib)",
    "TypeAliasType": "3.12 (typing)",
    "batched": "3.12 (itertools)",
    "override": "3.12 (typing)",
}

#: Builtins, which need no import and so must be caught on plain ``Name`` nodes.
#: Deliberately tiny -- every entry has to be a name no sane local would reuse.
FORBIDDEN_BUILTINS: dict[str, str] = {
    "ExceptionGroup": "3.11 builtin",
    "BaseExceptionGroup": "3.11 builtin",
}

#: Dotted paths. Used where the leaf name alone is ambiguous -- ``chdir`` has existed
#: on ``os`` since forever but arrived on ``contextlib`` in 3.11.
FORBIDDEN_ATTRIBUTES: dict[str, str] = {
    "datetime.UTC": "3.11 alias; use timezone.utc (app/clock.py already does)",
    "asyncio.TaskGroup": "3.11",
    "asyncio.Runner": "3.11",
    "asyncio.Barrier": "3.11",
    "asyncio.timeout": "3.11; use asyncio.wait_for",
    "contextlib.chdir": "3.11",
    "enum.StrEnum": "3.11",
    "enum.member": "3.11",
    "enum.nonmember": "3.11",
    "enum.global_enum": "3.11",
    "hashlib.file_digest": "3.11",
    "itertools.batched": "3.12",
    "math.cbrt": "3.11",
    "math.exp2": "3.11",
    "re.NOFLAG": "3.11",
    "typing.Self": "3.11",
    "typing.Never": "3.11",
    "typing.LiteralString": "3.11",
    "typing.override": "3.12",
    "typing.TypeAliasType": "3.12",
    "warnings.deprecated": "3.13",
    "os.process_cpu_count": "3.13",
    "Path.walk": "3.12",
    "inspect.getasyncgenstate": "3.12",
    "sqlite3.Connection.autocommit": "3.12",
}


def dotted_name(node: ast.AST) -> str | None:
    """``a.b.c`` for an Attribute/Name chain, else None.

    Anything else (a subscript, a call result) is left alone: guessing at the type
    of ``things[0].walk`` would produce noise, and the leaf-name table already
    covers the distinctive cases.
    """
    parts: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if not isinstance(current, ast.Name):
        return None
    parts.append(current.id)
    return ".".join(reversed(parts))


def version_violations(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_IMPORTED_NAMES:
                    found.append(
                        f"{path.name}:{node.lineno} imports {alias.name} "
                        f"({FORBIDDEN_IMPORTED_NAMES[root]})"
                    )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                qualified = f"{module}.{alias.name}"
                if alias.name in FORBIDDEN_IMPORTED_NAMES:
                    found.append(
                        f"{path.name}:{node.lineno} imports {qualified} "
                        f"({FORBIDDEN_IMPORTED_NAMES[alias.name]})"
                    )
                elif qualified in FORBIDDEN_ATTRIBUTES:
                    found.append(
                        f"{path.name}:{node.lineno} imports {qualified} "
                        f"({FORBIDDEN_ATTRIBUTES[qualified]})"
                    )
        elif isinstance(node, ast.Name):
            if node.id in FORBIDDEN_BUILTINS:
                found.append(
                    f"{path.name}:{node.lineno} uses {node.id} "
                    f"({FORBIDDEN_BUILTINS[node.id]})"
                )
        elif isinstance(node, ast.Attribute):
            dotted = dotted_name(node)
            if dotted is None:
                continue
            for candidate, note in FORBIDDEN_ATTRIBUTES.items():
                # endswith so `datetime.datetime.UTC` and a module-qualified
                # `stdlib.datetime.UTC` both match `datetime.UTC`.
                if dotted == candidate or dotted.endswith("." + candidate):
                    found.append(f"{path.name}:{node.lineno} uses {dotted} ({note})")

    return found


@pytest.mark.parametrize("path", APP_FILES, ids=lambda p: p.name)
def test_module_uses_no_post_3_10_stdlib_name(path: Path) -> None:
    violations = version_violations(path)
    assert violations == [], "\n".join(violations)


def test_the_scanner_actually_detects_something(tmp_path: Path) -> None:
    """A negative-only lint can pass because it is broken. This proves it bites.

    Written to a temporary file rather than into the package, so the check does not
    depend on the codebase containing a violation and cannot leave one behind.
    """
    sample = tmp_path / "baseline_probe.py"
    sample.write_text(
        "from enum import StrEnum\n"
        "from datetime import datetime\n"
        "import tomllib\n"
        "x = datetime.UTC\n"
        "try:\n"
        "    pass\n"
        "except ExceptionGroup:\n"
        "    pass\n",
        encoding="utf-8",
    )
    joined = "\n".join(version_violations(sample))

    assert "StrEnum" in joined
    assert "datetime.UTC" in joined
    assert "tomllib" in joined
    assert "ExceptionGroup" in joined


def test_the_scanner_does_not_flag_the_3_10_equivalents(tmp_path: Path) -> None:
    """The forms this codebase is supposed to use must come back clean.

    Without this, tightening a pattern until everything matches would still look
    like a passing lint.
    """
    sample = tmp_path / "baseline_clean.py"
    sample.write_text(
        "from datetime import datetime, timezone\n"
        "from enum import Enum\n"
        "import os\n"
        "\n"
        "class Status(str, Enum):\n"
        "    OK = 'OK'\n"
        "\n"
        "def now():\n"
        "    return datetime.now(timezone.utc)\n"
        "\n"
        "def override(value):\n"
        "    return os.chdir(value)\n",
        encoding="utf-8",
    )
    assert version_violations(sample) == []


# ---------------------------------------------------------------------------
# the declared target, in the three places it is written down
# ---------------------------------------------------------------------------


def test_running_interpreter_meets_the_target() -> None:
    assert sys.version_info[:2] >= TARGET_VERSION, (
        f"this build targets Python {TARGET_VERSION[0]}.{TARGET_VERSION[1]}+, "
        f"running {sys.version.split()[0]}"
    )


def test_pyproject_requires_the_target_version() -> None:
    """Read with a regex, not tomllib -- which is exactly the point.

    ``tomllib`` is a 3.11 addition, so a test that forbids it cannot use it.
    """
    text = (API_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    requires = re.search(r'requires-python\s*=\s*"([^"]+)"', text)
    assert requires, "pyproject.toml declares no requires-python"
    assert requires.group(1) == ">=3.10", requires.group(1)

    target = re.search(r'target-version\s*=\s*"py(\d)(\d+)"', text)
    assert target, "pyproject.toml sets no ruff target-version"
    assert (int(target.group(1)), int(target.group(2))) == TARGET_VERSION


def test_requirements_states_the_same_target() -> None:
    """The prose and the config must not drift.

    requirements.txt is where a human looks first; pyproject is where the tooling
    looks. A mismatch between them is how a build ends up "supporting" a version
    nobody tested.
    """
    text = (API_ROOT / "requirements.txt").read_text(encoding="utf-8")
    stated = re.search(r"CPython (\d)\.(\d+)", text)
    assert stated, "requirements.txt does not state a target interpreter"
    assert (int(stated.group(1)), int(stated.group(2))) == TARGET_VERSION


# ---------------------------------------------------------------------------
# the behavioural difference the name scan cannot see
# ---------------------------------------------------------------------------


def test_stored_timestamps_round_trip_on_the_target_interpreter() -> None:
    """3.10's ``fromisoformat`` only reads what ``isoformat`` writes.

    3.11 relaxed it to accept most of RFC 3339, including a trailing ``Z``. Code
    written on 3.11 that parses a ``Z``-suffixed timestamp raises ValueError on 3.10.
    This asserts the round trip the application actually performs.
    """
    written = clock.utc_now_iso()
    parsed = clock.parse_iso(written)
    assert parsed.tzinfo is not None
    assert parsed.isoformat() == written

    assert clock.parse_iso(clock.iso_plus_seconds(60)) > parsed


def test_clock_does_not_emit_a_z_suffix() -> None:
    """Because 3.10 could not read it back.

    Asserted on the writer rather than the reader: if the format ever changes to
    ``...Z``, this fails at the source instead of at whichever caller happens to
    parse it first.
    """
    for value in (clock.utc_now_iso(), clock.iso_plus_seconds(30)):
        assert not value.endswith("Z"), value
        assert "+00:00" in value, value


def test_naive_timestamps_are_rejected_rather_than_assumed_utc() -> None:
    """A guess here would silently shift an expiry by the local offset."""
    with pytest.raises(ValueError, match="no timezone"):
        clock.parse_iso("2026-08-22T12:00:00")


def test_ist_conversion_keeps_the_same_instant() -> None:
    """``handover_local_time`` is presentation only; it must not move the moment."""
    moment = clock.utc_now()
    assert clock.parse_iso(clock.to_ist_iso(moment)) == moment
    assert clock.to_ist_iso(moment).endswith("+05:30")
