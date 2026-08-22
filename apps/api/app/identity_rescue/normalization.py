from __future__ import annotations

import re
import unicodedata

_PUNCTUATION = re.compile(r"[^\w\s]", flags=re.UNICODE)
_WHITESPACE = re.compile(r"\s+")


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
