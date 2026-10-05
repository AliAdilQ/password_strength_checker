import pytest
from app.services.password_analyzer import analyze_password, strength_for_score


@pytest.mark.parametrize("sample,category", [
    ("123456", "Very Weak"), ("sunset42", "Weak"), ("Haze7trq", "Medium"),
    ("Haze9!tR", "Strong"), ("N8!vT2#xM7@qL4%z", "Very Strong"),
])
def test_all_strength_categories(sample, category):
    result = analyze_password(sample)
    assert result["strength"] == category
    assert 0 <= result["score"] <= 100


@pytest.mark.parametrize("score,category", [(0,"Very Weak"),(24,"Very Weak"),(25,"Weak"),(44,"Weak"),
    (45,"Medium"),(64,"Medium"),(65,"Strong"),(84,"Strong"),(85,"Very Strong"),(100,"Very Strong")])
def test_category_boundaries(score, category):
    assert strength_for_score(score) == category


@pytest.mark.parametrize("sample", ["password", "password123", "qwerty", "admin", "letmein", "welcome", "abc123"])
def test_common_password_penalty(sample):
    result = analyze_password(sample)
    assert result["score"] <= 10
    assert not result["checklist"]["not_common"]
    assert result["recommendations"]


@pytest.mark.parametrize("sample", ["P@ssw0rd123!", "P455w0rd123!", "Welcome2026!", "sunshine-P9!"])
def test_dictionary_and_substitutions_are_penalized(sample):
    result = analyze_password(sample)
    assert result["score"] <= 44
    assert not result["checklist"]["not_common"]


@pytest.mark.parametrize("sample", ["abcdefGH9!", "Qwerty987!", "Aaaa92!xyz", "aB9!aB9!aB9!", "987654T!y"])
def test_pattern_detection(sample):
    result = analyze_password(sample)
    assert not result["checklist"]["no_patterns"]
    assert any("sequences" in text for text in result["recommendations"])


def test_empty_password_and_unicode():
    assert analyze_password("")["score"] == 0
    result = analyze_password("é🛡M7!wKe2rF8")
    assert result["password_length"] == 12
    assert result["criteria"] == {"uppercase":True, "lowercase":True, "number":True, "symbol":True}


def test_result_never_contains_input():
    sample = "Synthetic-Only!v2-Q7mR"
    result = analyze_password(sample)
    assert "password" not in result
    assert sample not in str(result)


def test_long_passphrase_can_score_well_without_all_character_types():
    result = analyze_password("violet lantern pebble cedar")
    assert result["score"] >= 65
    assert result["criteria_passed"] < 8
