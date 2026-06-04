"""Lint a notification template against a known field list."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Set
from .parse import extract_refs, has_unclosed


@dataclass
class Template:
    subject: str
    body: str
    name: str = "notification"


@dataclass
class Finding:
    severity: str       # high | medium | low
    rule: str
    message: str


def lint_template(tpl: Template, valid_fields: Optional[Set[str]] = None,
                  mail_scripts: Optional[Set[str]] = None) -> List[Finding]:
    out: List[Finding] = []
    valid_fields = valid_fields or set()
    mail_scripts = mail_scripts or set()

    if not tpl.subject.strip():
        out.append(Finding("high", "empty-subject", "Subject line is empty."))
    if not tpl.body.strip():
        out.append(Finding("high", "empty-body", "Message body is empty."))

    full = tpl.subject + "\n" + tpl.body
    if has_unclosed(full):
        out.append(Finding("high", "unclosed-variable", "An unclosed ${ ... was found."))

    refs = extract_refs(full)
    for r in refs:
        if r.is_field_ref and valid_fields and r.field not in valid_fields:
            out.append(Finding("high", "unknown-field",
                f"References '{r.field}' which is not a field on the target table."))
        if r.kind == "mail_script" and mail_scripts and r.field not in mail_scripts:
            out.append(Finding("medium", "unknown-mail-script",
                f"Uses mail_script '{r.field}' which does not exist."))
        if r.kind == "unknown":
            out.append(Finding("medium", "malformed-ref",
                f"'{r.raw}' is not a recognizable variable reference."))

    # subject with no personalization is a soft smell for mass notifications
    if tpl.subject and "${" not in tpl.subject and len(tpl.subject) < 8:
        out.append(Finding("low", "static-subject", "Subject is short and has no variables."))

    sev = {"high": 0, "medium": 1, "low": 2}
    out.sort(key=lambda f: sev[f.severity])
    return out
