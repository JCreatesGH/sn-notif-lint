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


def test_unknown_field_suggests_typo_fix():
    tpl = Template(subject="x ${number}", body="priority is ${current.prioirty}")
    f = next(f for f in lint_template(tpl, FIELDS, SCRIPTS) if f.rule == "unknown-field")
    assert f.suggestion == "priority"
    assert "Did you mean 'priority'?" in f.message


def test_unknown_field_suggests_abbreviation_expansion():
    tpl = Template(subject="x ${number}", body="${short_desc}")
    f = next(f for f in lint_template(tpl, FIELDS, SCRIPTS) if f.rule == "unknown-field")
    assert f.suggestion == "short_description"


def test_unknown_field_no_suggestion_when_nothing_close():
    tpl = Template(subject="x ${number}", body="${current.xyzzy_qqq}")
    f = next(f for f in lint_template(tpl, FIELDS, SCRIPTS) if f.rule == "unknown-field")
    assert f.suggestion is None
    assert "Did you mean" not in f.message


def test_unknown_mail_script_suggests():
    tpl = Template(subject="x ${number}", body="${mail_script:greetng}")
    f = next(f for f in lint_template(tpl, FIELDS, SCRIPTS) if f.rule == "unknown-mail-script")
    assert f.suggestion == "greeting"


def test_multiline_subject_flagged():
    tpl = Template(subject="INC ${number}\nurgent", body="ok ${number}")
    assert "multiline-subject" in rules(lint_template(tpl, FIELDS))
