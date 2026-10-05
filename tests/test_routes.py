from pathlib import Path
import pytest
from sqlalchemy import inspect

from app.extensions import db
from app.models import PasswordCheck
from app.services.password_analyzer import analyze_password
from tests.conftest import csrf_token


@pytest.mark.parametrize("path", ["/", "/about", "/security-tips", "/admin/login"])
def test_public_pages(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert "Password Strength Checker" in response.text
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]


def test_api_returns_metadata_only_and_no_storage_by_default(app, client, caplog):
    synthetic = "Synthetic-Only!v2-Q7mR"
    response = client.post("/api/check-password", json={"password": synthetic})
    assert response.status_code == 200
    assert response.json == analyze_password(synthetic)
    assert synthetic not in response.text and synthetic not in caplog.text
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count(PasswordCheck.id))) == 0


def test_api_opt_in_stores_only_allowed_metadata(app, client):
    synthetic = "Synthetic-Only!v2-Q7mR"
    response = client.post("/api/check-password", json={"password": synthetic, "save_analytics": True})
    assert response.status_code == 200
    with app.app_context():
        records = db.session.scalars(db.select(PasswordCheck)).all()
        assert len(records) == 1
        assert records[0].score == response.json["score"]
        columns = {column["name"] for column in inspect(db.engine).get_columns("password_check")}
        assert columns == {"id", "strength", "score", "password_length", "has_uppercase", "has_lowercase", "has_number", "has_symbol", "created_at"}
        assert synthetic.encode() not in Path(db.engine.url.database).read_bytes()


@pytest.mark.parametrize("payload", [{}, {"password":""}, {"password":3}, {"password":None}, {"password":"x"*257},
    ["invalid"], {"password":"valid", "unexpected":True}, {"password":"valid", "save_analytics":"yes"}])
def test_api_rejects_invalid_input(client, payload):
    response = client.post("/api/check-password", json=payload)
    assert response.status_code == 400
    assert "error" in response.json


def test_api_rejects_non_json_and_malformed_json(client):
    assert client.post("/api/check-password", data="not JSON").status_code == 415
    assert client.post("/api/check-password", data="{broken", content_type="application/json").status_code == 400
    assert client.post("/api/check-password", data="x"*17000, content_type="application/json").status_code == 413


def test_metadata_endpoint_csrf_allowlist_and_save(app, client):
    payload = {"score":85, "password_length":16, "criteria":{"uppercase":True,"lowercase":True,"number":True,"symbol":True}}
    assert client.post("/api/analytics", json=payload).status_code == 400
    headers = {"X-CSRFToken":csrf_token(client)}
    assert client.post("/api/analytics", json={**payload, "password":"synthetic"}, headers=headers).status_code == 400
    assert client.post("/api/analytics", json={**payload, "score":True}, headers=headers).status_code == 400
    assert client.post("/api/analytics", json={**payload, "criteria":{}}, headers=headers).status_code == 400
    assert client.post("/api/analytics", json=payload, headers=headers).status_code == 201
    with app.app_context():
        record = db.session.scalar(db.select(PasswordCheck))
        assert record.strength == "Very Strong"
        assert record.password_length == 16


def test_custom_errors(client, app):
    assert client.get("/does-not-exist").status_code == 404
    assert "off the grid" in client.get("/does-not-exist").text
    assert client.get("/api/does-not-exist").json == {"error":"The page you're looking for doesn't exist. Let's get you back to safety."}


def test_forbidden_and_internal_error_pages(app, client):
    from flask import abort

    @app.get("/_test-forbidden")
    def forbidden():
        abort(403)

    @app.get("/_test-error")
    def internal_error():
        raise RuntimeError("Synthetic test failure")

    app.config["PROPAGATE_EXCEPTIONS"] = False
    forbidden_response = client.get("/_test-forbidden")
    assert forbidden_response.status_code == 403
    assert "A little extra protection" in forbidden_response.text
    error_response = client.get("/_test-error")
    assert error_response.status_code == 500
    assert "We hit a small roadblock" in error_response.text


@pytest.mark.parametrize("asset", ["css/style.css", "css/admin.css", "js/main.js", "js/password-checker.js", "js/password-generator.js", "js/admin.js", "data/scoring-rules.json", "vendor/bootstrap.min.css", "vendor/bootstrap-icons.min.css", "vendor/fonts/bootstrap-icons.woff2", "vendor/chart.umd.min.js", "images/favicon.svg"])
def test_bundled_assets(client, asset):
    assert client.get(f"/static/{asset}").status_code == 200
