"""Extract ${...} variable references from a notification template."""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List

_REF = re.compile(r"\$\{([^}]*)\}")
_OPEN = re.compile(r"\$\{[^}]*$")     # an unclosed ${ at end / line


@dataclass
class Ref:
    raw: str            # full inside ${...}
    kind: str           # field | current | mail_script | event | url | sys | unknown
    field: str          # resolved field name where applicable

    @property
    def is_field_ref(self) -> bool:
        return self.kind in ("field", "current")


def classify(inside: str) -> Ref:
    s = inside.strip()
    if s.startswith("mail_script:"):
        return Ref(s, "mail_script", s.split(":", 1)[1].strip())
    if s.startswith("current."):
        return Ref(s, "current", s[len("current."):])
    if s in ("URI", "URI_REF", "uri", "uri_ref"):
        return Ref(s, "url", s)
    if s.startswith("sys_") or s in ("event.parm1", "event.parm2"):
        return Ref(s, "sys", s)
    if re.fullmatch(r"[A-Za-z][\w.]*", s):
        return Ref(s, "field", s)
    return Ref(s, "unknown", s)


def extract_refs(text: str) -> List[Ref]:
    return [classify(m.group(1)) for m in _REF.finditer(text)]


def has_unclosed(text: str) -> bool:
    # a ${ with no following } on the same logical line
    for line in text.splitlines():
        # remove well-formed refs, then look for a stray ${
        stripped = _REF.sub("", line)
        if "${" in stripped:
            return True
    return False
