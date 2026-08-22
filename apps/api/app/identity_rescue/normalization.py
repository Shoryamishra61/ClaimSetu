from __future__ import annotations

import re
import unicodedata
from enum import Enum

_PUNCTUATION = re.compile(r"[^\w\s]", flags=re.UNICODE)
_WHITESPACE = re.compile(r"\s+")


class ComparisonResult(str, Enum):
    EXACT = "EXACT"
    RULE_COMPATIBLE = "RULE_COMPATIBLE"
    REVIEW = "REVIEW"
    MISMATCH = "MISMATCH"
    MISSING = "MISSING"


def normalize_text(value: str) -> str:
    """Return a conservative comparison form without changing the original."""
    unicode_value = unicodedata.normalize("NFKC", value)
    without_punctuation = _PUNCTUATION.sub(" ", unicode_value)
    return _WHITESPACE.sub(" ", without_punctuation).strip().casefold()


def name_tokens(value: str) -> tuple[str, ...]:
    normalized = normalize_text(value)
    return tuple(normalized.split()) if normalized else ()


def expand_controlled_tokens(
    tokens: tuple[str, ...], relations: dict[str, str]
) -> tuple[str, ...]:
    """Expand only fixture-declared relations; never guess what an initial means."""
    normalized_relations = {
        normalize_text(key): normalize_text(expansion)
        for key, expansion in relations.items()
    }
    return tuple(normalized_relations.get(token, token) for token in tokens)


def compare_names(
    left: str | None,
    right: str | None,
    *,
    controlled_relations: dict[str, str] | None = None,
    allow_token_reorder: bool = False,
    controlled_transliterations: set[tuple[str, str]] | None = None,
) -> ComparisonResult:
    """Compare full names conservatively under explicit, rule-scoped permissions."""
    if not left or not right:
        return ComparisonResult.MISSING
    left_normalized = normalize_text(left)
    right_normalized = normalize_text(right)
    if left_normalized == right_normalized:
        return ComparisonResult.EXACT

    controlled_pairs = {
        (normalize_text(first), normalize_text(second))
        for first, second in (controlled_transliterations or set())
    }
    if (left_normalized, right_normalized) in controlled_pairs or (
        right_normalized,
        left_normalized,
    ) in controlled_pairs:
        return ComparisonResult.RULE_COMPATIBLE

    relations = controlled_relations or {}
    left_tokens = expand_controlled_tokens(name_tokens(left), relations)
    right_tokens = expand_controlled_tokens(name_tokens(right), relations)
    if left_tokens == right_tokens:
        return ComparisonResult.RULE_COMPATIBLE
    if allow_token_reorder and sorted(left_tokens) == sorted(right_tokens):
        return ComparisonResult.RULE_COMPATIBLE

    if any(not token.isascii() for token in (*left_tokens, *right_tokens)):
        return ComparisonResult.REVIEW
    if any(len(token) == 1 for token in (*left_tokens, *right_tokens)):
        return ComparisonResult.REVIEW
    return ComparisonResult.MISMATCH


def compare_iso_dates(left: str | None, right: str | None) -> ComparisonResult:
    """Compare canonical ISO dates without guessing ambiguous regional formats."""
    if not left or not right:
        return ComparisonResult.MISSING
    iso_date = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
    if not iso_date.fullmatch(left) or not iso_date.fullmatch(right):
        return ComparisonResult.REVIEW
    return ComparisonResult.EXACT if left == right else ComparisonResult.MISMATCH
