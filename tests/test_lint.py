from notiflint import lint_template, Template


FIELDS = {"number", "short_description", "caller_id", "priority"}
SCRIPTS = {"greeting"}


def rules(findings):
    return {f.rule for f in findings}


def test_unknown_field_flagged():
    tpl = Template(subject="INC ${number}", body="Hi ${current.caller_id}, ${current.bogus_field}")
    r = rules(lint_template(tpl, FIELDS, SCRIPTS))
    assert "unknown-field" in r


def test_valid_template_clean():
    tpl = Template(subject="INC ${number}: ${short_description}",
                   body="Hello ${current.caller_id}, priority ${current.priority}. ${mail_script:greeting}")
    findings = lint_template(tpl, FIELDS, SCRIPTS)
    assert all(f.severity != "high" for f in findings)


def test_empty_subject_and_body():
    r = rules(lint_template(Template(subject="", body=""), FIELDS))
    assert "empty-subject" in r and "empty-body" in r


def test_unclosed_variable():
    tpl = Template(subject="INC ${number}", body="Hello ${current.caller_id")
    assert "unclosed-variable" in rules(lint_template(tpl, FIELDS))


def test_unknown_mail_script():
    tpl = Template(subject="x ${number}", body="${mail_script:does_not_exist}")
    assert "unknown-mail-script" in rules(lint_template(tpl, FIELDS, SCRIPTS))


def test_high_findings_first():
    tpl = Template(subject="", body="${current.bogus}")
    findings = lint_template(tpl, FIELDS)
    assert findings[0].severity == "high"


def test_dot_walk_validates_base_field_only():
    # caller_id is a valid reference field; dot-walking it must not flag unknown-field
    tpl = Template(subject="x ${number}", body="Hi ${current.caller_id.email}, ${caller_id.manager.name}")
    assert "unknown-field" not in rules(lint_template(tpl, FIELDS, SCRIPTS))
    # but a bogus base still flags
    bad = Template(subject="x ${number}", body="${current.nope.email}")
    assert "unknown-field" in rules(lint_template(bad, FIELDS, SCRIPTS))
