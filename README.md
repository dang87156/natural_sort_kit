# natural_sort_kit

Sort strings the way a person expects: `file2` before `file10`.

```python
from natural_sort_kit import natural_key, natural_sorted

names = ["file10.txt", "file2.txt", "file1.txt"]
print(natural_sorted(names))
# ['file1.txt', 'file2.txt', 'file10.txt']

# Or use the key directly with sorted():
print(sorted(names, key=natural_key))
# ['file1.txt', 'file2.txt', 'file10.txt']
```

## Why this exists

Plain lexicographic sorting puts `file10` before `file2`, which is rarely what a
human wants when looking at a directory listing.  Natural sort splits each string
into alternating text and integer chunks and compares them chunk by chunk, so digit
runs are ordered by numeric value.

The trade-off: this library is deliberately small and locale-agnostic.  It recognises
only ASCII digits (`0`-`9`) and compares text case-insensitively with the original
casing as a tie-breaker.  It does not normalise Unicode, does not consult the system
locale, and does not try to parse decimal points or signs as part of a number.  That
keeps the behaviour predictable across machines and makes the sort key a plain tuple
that you can inspect and test.

## The awkward edge

Leading zeros are ignored for the numeric comparison: `"007"` and `"7"` produce the
same key, so their relative order is whatever order they appeared in the input
(Python's sort is stable).  If you need a specific tie-break for equal numeric values,
sort with a secondary key of your own.

## API

- `natural_key(text: str) -> tuple` — return a sort key for one string.  Raises
  `TypeError` if `text` is not a `str`.
- `natural_sorted(iterable, *, reverse=False) -> list[str]` — return a new list of
  the input sorted naturally.  The input is not mutated.
