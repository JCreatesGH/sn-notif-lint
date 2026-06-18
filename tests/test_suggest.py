from notiflint import closest, levenshtein


def test_levenshtein_basics():
    assert levenshtein("priority", "priority") == 0
    assert levenshtein("prioirty", "priority") == 2   # transposition
    assert levenshtein("", "abc") == 3
    assert levenshtein("abc", "") == 3


FIELDS = {"number", "short_description", "caller_id", "priority", "assigned_to"}


def test_closest_exact_case_insensitive():
    assert closest("Priority", FIELDS) == "priority"


def test_closest_abbreviation_prefix():
    assert closest("short_desc", FIELDS) == "short_description"
    assert closest("assigned", FIELDS) == "assigned_to"


def test_closest_typo_within_distance():
    assert closest("prioirty", FIELDS) == "priority"
    assert closest("numbr", FIELDS) == "number"


def test_closest_returns_none_when_far():
    assert closest("xyzzy_qqq", FIELDS) is None
    assert closest("", FIELDS) is None


def test_closest_handles_empty_candidates():
    assert closest("priority", set()) is None
