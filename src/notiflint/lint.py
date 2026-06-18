"""Lint a notification template against a known field list."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Set
from .parse import extract_refs, has_unclosed
from .suggest import closest


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
    suggestion: Optional[str] = None   # nearest valid name, when one is likely


def lint_template(tpl: Template, valid_fields: Optional[Set[str]] = None,
                  mail_scripts: Optional[Set[str]] = None) -> List[Finding]:
    out: List[Finding] = []
    valid_fields = valid_fields or set()
    mail_scripts = mail_scripts or set()

    if not tpl.subject.strip():
        out.append(Finding("high", "empty-subject", "Subject line is empty."))
    if not tpl.body.strip():
        out.append(Finding("high", "empty-body", "Message body is empty."))

    # ServiceNow email subjects are a single header line; an embedded newline truncates it.
    if "\n" in tpl.subject or "\r" in tpl.subject:
        out.append(Finding("medium", "multiline-subject",
            "Subject contains a line break; ServiceNow truncates the subject at the first newline."))

    full = tpl.subject + "\n" + tpl.body
    if has_unclosed(full):
        out.append(Finding("high", "unclosed-variable", "An unclosed ${ ... was found."))

    refs = extract_refs(full)
    for r in refs:
        # Validate the base field only: a dot-walk like `caller_id.email` traverses a
        # reference, so checking the full path against a flat field list would false-positive.
        if r.is_field_ref and valid_fields and r.field.split(".")[0] not in valid_fields:
            base = r.field.split(".")[0]
            hint = closest(base, valid_fields)
            msg = f"References '{r.field}' which is not a field on the target table."
            if hint:
                msg += f" Did you mean '{hint}'?"
            out.append(Finding("high", "unknown-field", msg, suggestion=hint))
        if r.kind == "mail_script" and mail_scripts and r.field not in mail_scripts:
            hint = closest(r.field, mail_scripts)
            msg = f"Uses mail_script '{r.field}' which does not exist."
            if hint:
                msg += f" Did you mean '{hint}'?"
            out.append(Finding("medium", "unknown-mail-script", msg, suggestion=hint))
        if r.kind == "unknown":
            out.append(Finding("medium", "malformed-ref",
                f"'{r.raw}' is not a recognizable variable reference."))

    # subject with no personalization is a soft smell for mass notifications
    if tpl.subject and "${" not in tpl.subject and len(tpl.subject) < 8:
        out.append(Finding("low", "static-subject", "Subject is short and has no variables."))

    sev = {"high": 0, "medium": 1, "low": 2}
    out.sort(key=lambda f: sev[f.severity])
    return out
