"""Command-line interface: lint a ServiceNow notification template (JSON in)."""
from __future__ import annotations
import argparse
import json
import sys
from typing import List, Optional

from .lint import lint_template, Template


def _csv(v: Optional[str]):
    return {s.strip() for s in v.split(",") if s.strip()} if v else None


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="notiflint", description="Lint a ServiceNow notification template for broken refs.")
    parser.add_argument("file", nargs="?", help="JSON {subject, body, name?}; default stdin")
    parser.add_argument("--fields", help="comma-separated valid field names (from the dictionary)")
    parser.add_argument("--mail-scripts", help="comma-separated valid mail_script names")
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    args = parser.parse_args(argv)

    raw = open(args.file, encoding="utf-8").read() if args.file else sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("error: expected a JSON object with subject/body", file=sys.stderr)
        return 2

    tpl = Template(subject=data.get("subject", ""), body=data.get("body", ""),
                   name=data.get("name", "notification"))
    findings = lint_template(tpl, _csv(args.fields), _csv(args.mail_scripts))

    if args.json:
        print(json.dumps([f.__dict__ for f in findings], indent=2))
    elif not findings:
        print("✓ no issues")
    else:
        for f in findings:
            print(f"{f.severity.upper():6} {f.rule}: {f.message}")

    return 1 if any(f.severity == "high" for f in findings) else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
