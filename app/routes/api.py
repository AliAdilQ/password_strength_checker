"""Password API and opt-in browser metadata endpoint."""
from flask import Blueprint, jsonify, request

from app.extensions import csrf, db
from app.models import PasswordCheck
from app.services.password_analyzer import analyze_password, strength_for_score

api = Blueprint("api", __name__, url_prefix="/api")


def save_result(result):
    criteria = result["criteria"]
    record = PasswordCheck(
        strength=result["strength"], score=result["score"], password_length=result["password_length"],
        has_uppercase=criteria["uppercase"], has_lowercase=criteria["lowercase"],
        has_number=criteria["number"], has_symbol=criteria["symbol"],
    )
    db.session.add(record)
    db.session.commit()


@api.post("/check-password")
@csrf.exempt
def check_password():
    # Stateless JSON API: no authentication cookies used, no database writes by default.
    if not request.is_json:
        return jsonify(error="Send a JSON object with a password string."), 415
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or set(payload) - {"password", "save_analytics"}:
        return jsonify(error="Expected only password and optional save_analytics fields."), 400
    password = payload.get("password")
    if not isinstance(password, str) or not 1 <= len(password) <= 256:
        return jsonify(error="Password must be a string between 1 and 256 characters."), 400
    if "save_analytics" in payload and type(payload["save_analytics"]) is not bool:
        return jsonify(error="save_analytics must be a boolean."), 400
    should_save = payload.get("save_analytics", False)
    result = analyze_password(password)
    del password
    payload.clear()
    if should_save:
        save_result(result)
    return jsonify(result)


@api.post("/analytics")
def analytics():
    """Accept a strict allowlist of metadata; reject any extra fields (including passwords)."""
    payload = request.get_json(silent=True)
    allowed = {"score", "password_length", "criteria"}
    if not isinstance(payload, dict) or set(payload) != allowed:
        return jsonify(error="Send only score, password_length, and criteria metadata."), 400
    score, length, criteria = payload["score"], payload["password_length"], payload["criteria"]
    if type(score) is not int or not 0 <= score <= 100 or type(length) is not int or not 1 <= length <= 256:
        return jsonify(error="Score or length is outside the allowed range."), 400
    if not isinstance(criteria, dict) or set(criteria) != {"uppercase", "lowercase", "number", "symbol"}:
        return jsonify(error="Provide the four character-type flags."), 400
    if any(type(value) is not bool for value in criteria.values()):
        return jsonify(error="Character-type flags must be booleans."), 400
    save_result({**payload, "strength": strength_for_score(score)})
    return jsonify(message="Anonymous result saved. Your password stayed in your browser."), 201
