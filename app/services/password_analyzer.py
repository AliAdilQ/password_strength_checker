"""Deterministic heuristic scoring. Inputs are processed in memory and never retained."""
import json
import re
from pathlib import Path

RULES = json.loads((Path(__file__).parents[1] / "static" / "data" / "scoring-rules.json").read_text(encoding="utf-8"))
CATEGORIES = ["Very Weak", "Weak", "Medium", "Strong", "Very Strong"]


def strength_for_score(score):
    return CATEGORIES[sum(score >= threshold for threshold in (25, 45, 65, 85))]


def analyze_password(password):
    """Return safe metadata only; never echo, hash, or persist the supplied input."""
    length = len(password)
    lower = password.lower()
    criteria = {
        "uppercase": bool(re.search(r"[A-Z]", password)),
        "lowercase": bool(re.search(r"[a-z]", password)),
        "number": bool(re.search(r"[0-9]", password)),
        "symbol": bool(re.search(r"[^A-Za-z0-9\s]", password)),
    }
    # ASCII character classes are intentional and match the browser scorer.
    normalized = lower.translate(str.maketrans({"@": "a", "0": "o", "4": "a", "3": "e", "1": "i", "5": "s", "7": "t", "$": "s", "!": "i"}))
    common = lower in RULES["common_passwords"]
    dictionary = any(word in lower or word in normalized for word in RULES["dictionary_words"])
    sequential = any(
        sequence[i:i + 4] in lower or sequence[i:i + 4][::-1] in lower
        for sequence in RULES["sequences"] for i in range(len(sequence) - 3)
    )
    repeated = bool(re.search(r"(.)\1{2,}", password))
    repeated_pattern = bool(re.fullmatch(r"(.{1,4})\1{2,}", password))
    low_diversity = length >= 8 and len(set(lower)) / length < 0.35
    predictable = bool(re.search(r"(?:19|20)\d{2}[!@#$%]*$", lower))
    no_patterns = not (sequential or repeated or repeated_pattern or low_diversity)
    score = next((points for minimum, points in RULES["length_points"] if length >= minimum), 0)
    score += sum(criteria.values()) * 10
    if length >= 8 and len(set(password)) >= min(length, 10):
        score += 10
    if length >= 12 and no_patterns and not dictionary:
        score += 10
    score -= 20 * sequential + 20 * repeated + 25 * repeated_pattern + 20 * low_diversity
    score -= 30 * dictionary + 10 * predictable
    score = max(0, min(100, score)) if length else 0
    if length < 8:
        score = min(score, 24)
    if common:
        score = min(score, 10)
    if dictionary:
        score = min(score, 44)
    checklist = {
        "minimum_length": length >= 8, "recommended_length": length >= 12,
        **criteria, "no_patterns": no_patterns and length > 0,
        "not_common": not common and not dictionary and length > 0,
    }
    recommendations = []
    if length < 12:
        recommendations.append("Make it longer. Aim for at least 12–16 characters.")
    if common or dictionary:
        recommendations.append("Replace common words and predictable substitutions with unrelated words or random characters.")
    if not no_patterns:
        recommendations.append("Avoid sequences, keyboard runs, and repeated characters or short blocks.")
    if predictable:
        recommendations.append("Avoid a year or date at the end of your password.")
    if sum(criteria.values()) < 3:
        recommendations.append("Try a mix of character types, or a longer randomly chosen passphrase.")
    if 0 < score < 85 and not recommendations:
        recommendations.append("Add length or use the generator for a less predictable password.")
    return {
        "score": score, "strength": strength_for_score(score), "password_length": length,
        "criteria": criteria, "checklist": checklist,
        "criteria_passed": sum(checklist.values()), "recommendations": recommendations,
    }
