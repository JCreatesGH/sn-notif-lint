from notiflint import extract_refs
from notiflint.parse import has_unclosed


def test_classifies_refs():
    refs = extract_refs("Hi ${current.caller_id}, ticket ${number} ${mail_script:greeting} ${URI}")
    kinds = {(r.kind, r.field) for r in refs}
    assert ("current", "caller_id") in kinds
    assert ("field", "number") in kinds
    assert ("mail_script", "greeting") in kinds
    assert ("url", "URI") in kinds


def test_unclosed_detection():
    assert has_unclosed("Hello ${current.name")
    assert not has_unclosed("Hello ${current.name}")
