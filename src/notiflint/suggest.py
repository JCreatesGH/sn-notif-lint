"""Suggest the closest valid name for a typo'd / abbreviated reference."""
from __future__ import annotations
from typing import Iterable, Optional


def levenshtein(a: str, b: str) -> int:
    """Classic edit distance (insert/delete/substitute)."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(
                prev[j] + 1,        # deletion
                cur[j - 1] + 1,     # insertion
                prev[j - 1] + (ca != cb),  # substitution
            ))
        prev = cur
    return prev[-1]


def closest(word: str, candidates: Iterable[str], max_distance: int = 2) -> Optional[str]:
    """Return the most likely intended candidate for `word`, or None.

    Matches, in priority order: an exact case-insensitive hit (e.g. ``Number`` →
    ``number``), an abbreviation/prefix relationship in either direction
    (``short_desc`` → ``short_description``), then the nearest by edit distance
    (``prioirty`` → ``priority``). Returns None when nothing is close enough, so
    callers never surface a misleading guess.
    """
    word = word.strip()
    if not word:
        return None
    lw = word.lower()
    cands = [c for c in candidates if c]
    if not cands:
        return None

    # 1. exact, case-insensitive
    for c in cands:
        if c.lower() == lw:
            return c

    # 2. prefix / abbreviation, in either direction (needs a few chars to be meaningful)
    if len(lw) >= 3:
        prefix = [c for c in cands
                  if c.lower().startswith(lw) or lw.startswith(c.lower())]
        if prefix:
            # shortest extra distance = closest in length to the typed word
            return min(prefix, key=lambda c: (abs(len(c) - len(word)), c))

    # 3. nearest by edit distance, within a length-scaled threshold
    limit = max(max_distance, len(lw) // 3)
    scored = sorted(((levenshtein(lw, c.lower()), c) for c in cands), key=lambda t: (t[0], t[1]))
    dist, best = scored[0]
    return best if dist <= limit else None
