# notiflint — ServiceNow notification linter

[![CI](https://github.com/JCreatesGH/sn-notif-lint/actions/workflows/ci.yml/badge.svg)](https://github.com/JCreatesGH/sn-notif-lint/actions)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Stop shipping blank or broken notification emails. `notiflint` scans ServiceNow notification/email templates for variable references that won't resolve — misspelled fields, unclosed `${`, missing mail scripts — before they reach an inbox. When it finds a typo or abbreviation, it tells you the fix: `${current.prioirty}` → **"Did you mean 'priority'?"**, `${short_desc}` → `short_description`.

![screenshot](assets/screenshot.png)

## Install

```bash
pip install notiflint
```

## Use it

```python
from notiflint import lint_template, Template

tpl = Template(
    subject="INC ${number}: ${short_desc}",
    body="Hi ${current.caller_id}, priority ${current.prioirty}. ${mail_script:signature",
)

valid_fields = {"number", "short_description", "caller_id", "priority"}  # from the dictionary
mail_scripts = {"greeting"}

for f in lint_template(tpl, valid_fields, mail_scripts):
    print(f.severity, f.rule, f.message)
```

## What it catches

| Severity | Rule | Why |
|----------|------|-----|
| HIGH | `unknown-field` | `${short_desc}` / `${current.prioirty}` typos that render blank — **with a suggested fix** |
| HIGH | `empty-subject` / `empty-body` | the template would send nothing |
| HIGH | `unclosed-variable` | a stray `${` with no closing `}` |
| MEDIUM | `unknown-mail-script` | `${mail_script:x}` where `x` doesn't exist — **with a suggested fix** |
| MEDIUM | `multiline-subject` | a newline in the subject; ServiceNow truncates it at the first line break |
| MEDIUM | `malformed-ref` | unrecognizable `${…}` content |

It understands the ServiceNow reference styles — `${current.field}`, `${field}`, `${mail_script:name}`, `${URI}` / `${URI_REF}`, and `sys_*` / event params — and only validates the ones that should map to a real field. **Dot-walks** like `${current.caller_id.email}` are validated by their *base* field (`caller_id`), so traversing a reference doesn't trigger a false `unknown-field`.

### Did-you-mean suggestions

Every `unknown-field` and `unknown-mail-script` finding carries a `suggestion` (also in the
`--json` output) when a likely intended name exists. The matcher handles case (`Number` →
`number`), abbreviations and prefixes (`short_desc` → `short_description`, `assigned` →
`assigned_to`), and edit-distance typos (`prioirty` → `priority`) — and stays silent when
nothing is genuinely close, so it never invents a misleading guess.

```python
from notiflint import closest
closest("prioirty", {"priority", "number", "caller_id"})   # -> "priority"
```

## CLI

Installing the package adds a `notiflint` command — feed it a template as JSON (`{subject, body}`):

```bash
$ notiflint template.json --fields number,caller_id,priority --mail-scripts greeting
$ cat template.json | notiflint --json          # exits 1 on a HIGH issue (CI gate)
```

## Development

```bash
pip install -e .[dev] && python -m pytest -q   # 24 tests
```

## License

MIT
