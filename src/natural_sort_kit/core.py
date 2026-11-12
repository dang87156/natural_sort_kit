"""Core natural sort implementation.

Natural sorting orders digit runs numerically, so ``file2`` sorts before
``file10``.  We split a string into a list of alternating text and integer
chunks and compare chunk by chunk.  Text chunks are compared
case-insensitively (a common user expectation for file names) but ties are
broken by the original, case-sensitive text so the result is total and
stable.

Design decision: we do not attempt to normalise Unicode digits or handle
locale-specific collation.  The input is treated as a sequence of code
points; ASCII digits are the only digits recognised.  This keeps the
implementation small and predictable, and matches the behaviour of the
natural sort used by most file managers on ASCII-ish names.
"""

from __future__ import annotations

import re
from typing import Iterable, List, Sequence, Tuple, Union

__all__ = ["natural_key", "natural_sorted"]

# A chunk is either a string (text) or an int (a numeric run).
Chunk = Union[str, int]

# Match one or more ASCII digits.  Using an explicit character class rather
# than \d avoids matching non-ASCII digits that int() would reject or that
# would compare inconsistently.
_DIGIT_RE = re.compile(r"[0-9]+")


def _split(text: str) -> List[Chunk]:
    """Split *text* into alternating text and integer chunks.

    Empty text chunks are omitted.  A leading digit run produces an int as
    the first chunk.  The returned list is never empty for non-empty input;
    for empty input it is empty.
    """
    chunks: List[Chunk] = []
    pos = 0
    for match in _DIGIT_RE.finditer(text):
        start, end = match.span()
        if start > pos:
            chunks.append(text[pos:start])
        chunks.append(int(match.group()))
        pos = end
    if pos < len(text):
        chunks.append(text[pos:])
    return chunks


def _chunk_key(chunk: Chunk) -> Tuple[int, object]:
    """Return a sort key for a single chunk.

    The first element of the tuple is a type rank so that ints and strs are
    never compared directly (which would raise TypeError in Python 3).
    Numeric chunks sort before text chunks at the same position, which gives
    a deterministic order for e.g. ``"1"`` vs ``"a"``.

    For text chunks we return a tuple of (lowercased, original) so that a
    case-insensitive primary comparison is used, with the original casing as
    a tie-breaker.
    """
    if isinstance(chunk, int):
        return (0, chunk)
    return (1, (chunk.lower(), chunk))


def natural_key(text: str) -> Tuple[Tuple[int, object], ...]:
    """Return a sort key for *text* implementing natural ordering.

    The key is a tuple of per-chunk keys, suitable for passing to
    ``sorted(..., key=natural_key)``.  It is deterministic and total for
    strings: two different strings always produce different keys, because
    the original text is embedded in every text chunk's key.

    Raises TypeError if *text* is not a str.
    """
    if not isinstance(text, str):
        raise TypeError("natural_key expects a str, got %r" % type(text).__name__)
    return tuple(_chunk_key(c) for c in _split(text))


def natural_sorted(
    iterable: Iterable[str], *, reverse: bool = False
) -> List[str]:
    """Return a new list of *iterable* sorted naturally.

    This is a thin wrapper around ``sorted(iterable, key=natural_key)``.
    It exists so callers do not have to import the key function separately,
    and so the keyword-only ``reverse`` flag is documented in one place.
    """
    return sorted(iterable, key=natural_key, reverse=reverse)
