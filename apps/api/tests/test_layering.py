"""The dependency direction, enforced by reading the imports.

Three package docstrings promise this file. ``app/domain/__init__.py``: "Nothing in
this package may import from ``app.adapters`` or ``app.api``." ``app/db/__init__.py``:
"Only ``app.services`` may open a transaction." ``app/services/__init__.py`` draws
the graph. This is where those sentences become checks.

**Why bother.** The layering is not decoration -- it is what makes the rest of the
test suite trustworthy. Every invariant test in ``test_invariants.py`` calls services
directly and every policy test calls the domain with no database at all. That is only
possible because ``app.domain`` is a pure core. One import of ``app.db`` from a domain
module would not break anything visibly; it would quietly make the domain
untestable-in-isolation, and the next person would reach for a fixture instead of a
function call.

**How the resolution works.** Relative imports are resolved to absolute module paths
the way Python does it -- ``level`` dots up from the *package* the module lives in --
because a lint that treats ``from ..policy_types import X`` as a string cannot tell
which package it lands in. That distinction is not academic: it is exactly the bug
this file found in ``app/domain/policies/draft/gsr_649e_2026_draft.py``, where ``..``
resolved one level short of ``app.domain`` and named a module that does not exist.
Hence ``test_every_relative_import_resolves_to_a_real_module``, which is about
correctness rather than layering but belongs to the same walk.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.config import REPO_ROOT

APP_ROOT = REPO_ROOT / "apps" / "api" / "app"

#: Which packages each layer may import from, as top-level ``app`` subpackages or
#: modules. A module may always import from its own package.
#:
#: Read as "this layer's outward reach". The two empty-ish entries are the load-bearing
#: ones: ``domain`` and ``adapters`` reach nowhere, which is what makes them testable
#: and swappable respectively.
ALLOWED_DEPENDENCIES: dict[str, frozenset[str]] = {
    # A pure core. Not even clock or errors: a policy evaluator that needed the
    # current time would be a policy evaluator that could not be tested with a
    # literal, and an exception type shared with the transport layer is how HTTP
    # concerns leak into rules.
    "domain": frozenset(),
    # The simulated government boundary. Knows nothing about the product, so it
    # cannot start enforcing product rules and it can be replaced wholesale.
    "adapters": frozenset(),
    # Storage depends on the state graph (it validates transitions in SQL predicates)
    # and on the clock. Never on a service, an adapter, or the transport.
    "db": frozenset({"domain", "clock"}),
    # The only layer that may open a transaction, so it may see everything below it.
    "services": frozenset({"domain", "adapters", "db", "config", "clock", "errors"}),
    # Transport. Reaches services for behaviour, and db/adapters for types and copy
    # only -- asserted separately by the connection-argument test below.
    "api": frozenset(
        {"services", "domain", "db", "adapters", "copy", "errors", "clock", "config"}
    ),
}

def module_name(path: Path) -> str:
    """``app.services.case_service`` for ``.../app/services/case_service.py``."""
    relative = path.relative_to(APP_ROOT.parent).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def package_of(module: str) -> str:
    """The package a module lives in, which is what ``level`` counts up from.

    ``app.services.case_service`` -> ``app.services``; the package ``app.services``
    (i.e. its ``__init__``) -> ``app.services`` itself.
    """
    path = APP_ROOT.parent / Path(*module.split("."))
    if path.is_dir():
        return module
    return module.rsplit(".", 1)[0] if "." in module else ""


def resolve(module: str, node: ast.ImportFrom) -> list[str]:
    """Absolute targets of one ``from ... import ...`` statement.

    Returns both the module and each imported name qualified onto it, because
    ``from ..db import repository`` and ``from ..db.repository import CaseRow`` are the
    same dependency and must be seen as such.
    """
    base = node.module or ""
    if not node.level:
        return [base] if base else []

    package = package_of(module).split(".")
    if node.level - 1 > len(package):
        return [f"<unresolvable:{'.' * node.level}{base}>"]
    anchor = package[: len(package) - (node.level - 1)]
    target = ".".join([*anchor, base]) if base else ".".join(anchor)
    return [target, *(f"{target}.{alias.name}" for alias in node.names)]


def app_imports(path: Path) -> list[tuple[int, str]]:
    """Every ``app.*`` module this file depends on, as (line, absolute dotted name)."""
    module = module_name(path)
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend(
                (node.lineno, alias.name)
                for alias in node.names
                if alias.name == "app" or alias.name.startswith("app.")
            )
        elif isinstance(node, ast.ImportFrom):
            for target in resolve(module, node):
                if target.startswith("<unresolvable") or target.startswith("app"):
                    found.append((node.lineno, target))
    return found


def layer_of(module: str) -> str:
    """``services`` for ``app.services.case_service``; ``""`` for ``app.clock``."""
    parts = module.split(".")
    if len(parts) < 2 or parts[0] != "app":
        return ""
    return parts[1] if len(parts) > 2 or (APP_ROOT / parts[1]).is_dir() else ""


def top_level_target(module: str) -> str:
    """The ``app`` child a dependency belongs to: ``db`` for ``app.db.repository``."""
    parts = module.split(".")
    return parts[1] if len(parts) > 1 else ""


APP_FILES = sorted(p for p in APP_ROOT.rglob("*.py") if "__pycache__" not in p.parts)
LAYER_FILES = {
    layer: [p for p in APP_FILES if layer_of(module_name(p)) == layer]
    for layer in ALLOWED_DEPENDENCIES
}


def test_every_layer_has_files() -> None:
    """Guards against the whole file passing because a glob went wrong."""
    for layer, files in LAYER_FILES.items():
        assert files, f"no modules found for layer {layer!r} under {APP_ROOT}"


# ---------------------------------------------------------------------------
# resolution correctness -- the walk has to be right before its verdict means anything
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", APP_FILES, ids=lambda p: p.name)
def test_every_relative_import_resolves_to_a_real_module(path: Path) -> None:
    """A relative import one level short names a module that does not exist.

    Python raises ``ModuleNotFoundError`` at import time, which in a test suite shows
    up as a whole file failing to collect. Worth catching structurally, because a
    module that is only imported by one test (a documented-but-inert draft policy, for
    instance) can carry the fault for a long time without anyone importing it.
    """
    root = APP_ROOT.parent
    offences: list[str] = []
    for lineno, target in app_imports(path):
        if target.startswith("<unresolvable"):
            offences.append(f"{path.name}:{lineno} {target} escapes the package root")
            continue
        parts = target.split(".")
        if not (
            (root / Path(*parts)).is_dir()
            or (root / Path(*parts)).with_suffix(".py").is_file()
            # The last segment may be a name inside a module rather than a module.
            or (root / Path(*parts[:-1])).with_suffix(".py").is_file()
            or (root / Path(*parts[:-1])).is_dir()
        ):
            offences.append(f"{path.name}:{lineno} imports {target}, which does not exist")
    assert offences == [], "\n".join(offences)


def test_the_resolver_counts_levels_from_the_package() -> None:
    """Pins the semantics the previous test depends on.

    ``from ..policy_types import X`` means ``app.domain.policy_types`` in
    ``app/domain/policies/registry.py`` and ``app.domain.policies.policy_types`` in
    ``app/domain/policies/draft/gsr_649e_2026_draft.py``. Same text, different target.
    A resolver that got this wrong would either miss the real bug or invent one.
    """
    node = ast.parse("from ..policy_types import PolicyDefinition").body[0]
    assert isinstance(node, ast.ImportFrom)

    from_policies = resolve("app.domain.policies.registry", node)
    assert from_policies[0] == "app.domain.policy_types"

    from_draft = resolve("app.domain.policies.draft.gsr_649e_2026_draft", node)
    assert from_draft[0] == "app.domain.policies.policy_types"


def test_the_resolver_handles_a_package_init() -> None:
    """``app/db/__init__.py``'s ``from .connection import Database`` is ``app.db.connection``."""
    node = ast.parse("from .connection import Database").body[0]
    assert isinstance(node, ast.ImportFrom)
    assert resolve("app.db", node)[0] == "app.db.connection"


# ---------------------------------------------------------------------------
# the direction itself
# ---------------------------------------------------------------------------


@pytest.mark.invariant
@pytest.mark.parametrize("path", APP_FILES, ids=lambda p: p.name)
def test_module_only_imports_its_allowed_layers(path: Path) -> None:
    layer = layer_of(module_name(path))
    if layer not in ALLOWED_DEPENDENCIES:
        # app/main.py, app/clock.py and friends: the entry point and the leaves.
        # main.py is allowed to see everything, which is what makes it the entry point.
        return

    allowed = ALLOWED_DEPENDENCIES[layer] | {layer}
    offences = [
        f"{path.name}:{lineno} imports {target} -- layer {layer!r} may only reach "
        f"{sorted(allowed)}"
        for lineno, target in app_imports(path)
        if (child := top_level_target(target))
        and child not in allowed
        and child not in {"__init__"}
    ]
    assert offences == [], "\n".join(offences)


@pytest.mark.invariant
def test_the_domain_is_a_closed_pure_core() -> None:
    """Stated as one assertion because it is the single most load-bearing rule.

    Everything the domain needs is passed to it. That is why ``test_policy_current.py``
    can build a ``PolicyContext`` from a literal dict and assert real product rules
    with no database, no adapter and no application.
    """
    offences = [
        f"{path.name}:{lineno} imports {target}"
        for path in LAYER_FILES["domain"]
        for lineno, target in app_imports(path)
        if top_level_target(target) != "domain"
    ]
    assert offences == [], (
        "app.domain must import nothing else in the application:\n" + "\n".join(offences)
    )


@pytest.mark.invariant
def test_the_simulated_boundary_is_closed_too() -> None:
    """Adapters know nothing about the product they are wrapped in.

    So "replace the simulation with something real" stays a single-package change,
    and -- more importantly here -- an adapter cannot start enforcing a product rule
    that the invariant tests believe lives in the domain.
    """
    offences = [
        f"{path.name}:{lineno} imports {target}"
        for path in LAYER_FILES["adapters"]
        for lineno, target in app_imports(path)
        if top_level_target(target) != "adapters"
    ]
    assert offences == [], "\n".join(offences)


@pytest.mark.invariant
def test_nothing_imports_the_application_entry_point() -> None:
    """``app.main`` composes; it is not a library.

    An import of ``app.main`` from inside a layer would create a cycle and would make
    ``create_app`` a dependency of the thing it is supposed to assemble.
    """
    offences = [
        f"{module_name(path)}:{lineno} imports {target}"
        for path in APP_FILES
        if module_name(path) != "app.main"
        for lineno, target in app_imports(path)
        if target == "app.main" or target.startswith("app.main.")
    ]
    assert offences == [], "\n".join(offences)


# ---------------------------------------------------------------------------
# transaction ownership -- the rule db/__init__.py actually states
# ---------------------------------------------------------------------------


def transaction_openings(path: Path) -> list[int]:
    """Lines calling ``<something>.db.read()`` or ``.db.write()``."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = node.func
        if not isinstance(target, ast.Attribute) or target.attr not in {"read", "write"}:
            continue
        owner = target.value
        if isinstance(owner, ast.Attribute) and owner.attr == "db":
            found.append(node.lineno)
    return found


@pytest.mark.invariant
@pytest.mark.parametrize("path", APP_FILES, ids=lambda p: p.name)
def test_only_services_open_a_transaction(path: Path) -> None:
    """The rule that makes api-importing-db harmless.

    A route that opened its own transaction could commit a state change without going
    through the compare-and-set transitions the state machine relies on. Keeping the
    boundary in one layer is what makes "no client can select a state" checkable.
    """
    if layer_of(module_name(path)) == "services":
        return
    lines = transaction_openings(path)
    assert lines == [], (
        f"{path.name} opens a transaction at line(s) {lines}; only app.services may"
    )


@pytest.mark.invariant
def test_services_do_open_transactions() -> None:
    """Otherwise the test above could pass because the scanner matches nothing."""
    total = sum(len(transaction_openings(p)) for p in LAYER_FILES["services"])
    assert total >= 10, f"scanner found only {total} transaction openings in services"


@pytest.mark.invariant
@pytest.mark.parametrize("path", LAYER_FILES["api"], ids=lambda p: p.name)
def test_no_transport_function_accepts_a_connection(path: Path) -> None:
    """``app.api`` may name a row type; it may not be handed a live connection.

    This is the assertion that makes ``app.api`` importing ``app.db`` a typing
    convenience rather than a layering breach. Checked on annotations, since that is
    how a connection would arrive.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    offences: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        arguments = [
            *node.args.posonlyargs,
            *node.args.args,
            *node.args.kwonlyargs,
        ]
        for argument in arguments:
            if argument.annotation is None:
                continue
            rendered = ast.unparse(argument.annotation)
            if "Connection" in rendered or "sqlite3" in rendered:
                offences.append(
                    f"{path.name}:{node.lineno} {node.name}({argument.arg}: {rendered})"
                )
    assert offences == [], "\n".join(offences)


# ---------------------------------------------------------------------------
# the docstrings that promise all of the above
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "package", ["domain", "db", "services", "adapters"], ids=lambda s: s
)
def test_each_layer_documents_its_own_rule(package: str) -> None:
    """A layer whose ``__init__`` says nothing invites the next author to guess.

    Cheap to assert, and it means the rule and the test cannot drift apart without one
    of them failing: the docstring names this file, and this file names the docstring.
    """
    text = (APP_ROOT / package / "__init__.py").read_text(encoding="utf-8")
    assert text.lstrip().startswith('"""'), f"{package}/__init__.py has no docstring"
    assert "test_layering.py" in text or "test_no_live_integration.py" in text, (
        f"{package}/__init__.py states no enforced rule"
    )
