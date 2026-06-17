import json
from notiflint.cli import main


def _tpl(tmp_path, obj):
    f = tmp_path / "tpl.json"
    f.write_text(json.dumps(obj))
    return str(f)


def test_cli_flags_unknown_field_and_exits_1(tmp_path, capsys):
    path = _tpl(tmp_path, {"subject": "INC ${number}", "body": "Hi ${current.bogus}"})
    code = main([path, "--fields", "number,caller_id"])
    out = capsys.readouterr().out
    assert code == 1
    assert "unknown-field" in out


def test_cli_clean_exits_0(tmp_path, capsys):
    path = _tpl(tmp_path, {"subject": "INC ${number}", "body": "Hi ${current.caller_id}"})
    code = main([path, "--fields", "number,caller_id"])
    assert code == 0
    assert "no issues" in capsys.readouterr().out


def test_cli_json(tmp_path, capsys):
    path = _tpl(tmp_path, {"subject": "", "body": ""})
    assert main([path, "--json"]) == 1
    data = json.loads(capsys.readouterr().out)
    assert {f["rule"] for f in data} >= {"empty-subject", "empty-body"}


def test_cli_rejects_non_object(tmp_path, capsys):
    f = tmp_path / "bad.json"
    f.write_text("[1,2,3]")
    assert main([str(f)]) == 2
    assert "expected a JSON object" in capsys.readouterr().err
