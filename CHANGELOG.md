# Changelog

All notable changes to this project are documented here. This project adheres to
[Semantic Versioning](https://semver.org/).

## [0.2.0]

### Added
- **Did-you-mean suggestions.** `unknown-field` and `unknown-mail-script` findings now carry
  a `suggestion` with the most likely intended name. The matcher (`notiflint.closest`)
  handles case differences (`Number` → `number`), abbreviations/prefixes (`short_desc` →
  `short_description`, `assigned` → `assigned_to`), and edit-distance typos (`prioirty` →
  `priority`), and returns nothing when no candidate is genuinely close.
- New `multiline-subject` rule (medium): a line break in the subject is flagged because
  ServiceNow truncates the subject at the first newline.
- Public API now exports `closest` and `levenshtein`; `Finding` gained a `suggestion` field
  (also surfaced in `--json`).

## [0.1.0]

- Initial release: lint ServiceNow notification templates for `unknown-field`,
  `empty-subject`/`empty-body`, `unclosed-variable`, `unknown-mail-script`, and
  `malformed-ref`, with dot-walk-aware field validation and a CLI that exits non-zero on
  any HIGH finding.
