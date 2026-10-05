from app.extensions import db
from app.models import Admin, PasswordCheck
from seed import seed_database
from tests.conftest import csrf_token, login


def test_dashboard_requires_login(client):
    response = client.get("/admin/dashboard")
    assert response.status_code == 302
    assert "/admin/login" in response.location
    assert client.get("/admin/stats").status_code == 302


def test_valid_login_and_dashboard(client, app):
    assert login(client).status_code == 302
    response = client.get("/admin/dashboard")
    assert response.status_code == 200
    assert "Security at a glance" in response.text
    assert "A clean slate" in response.text
    assert client.get("/admin/stats").json["total"] == 0
    with app.app_context():
        account = db.session.scalar(db.select(Admin))
        assert account.password_hash.startswith("scrypt:")
        assert account.password_hash != "Admin@12345"


def test_invalid_login(client):
    token = csrf_token(client, "/admin/login")
    response = client.post("/admin/login", data={"username":"admin", "password":"wrong", "csrf_token":token})
    assert response.status_code == 401
    assert "incorrect" in response.text
    assert client.get("/admin/dashboard").status_code == 302


def test_unknown_username_is_rejected(client):
    token = csrf_token(client, "/admin/login")
    assert client.post("/admin/login", data={"username":"unknown", "password":"wrong", "csrf_token":token}).status_code == 401


def test_login_and_logout_require_csrf(client):
    assert client.post("/admin/login", data={"username":"admin","password":"Admin@12345"}).status_code == 400
    login(client)
    assert client.post("/admin/logout").status_code == 400
    assert client.get("/admin/logout").status_code == 405
    token = csrf_token(client, "/admin/dashboard")
    assert client.post("/admin/logout", data={"csrf_token":token}).status_code == 302
    assert client.get("/admin/dashboard").status_code == 302


def test_session_cookie_is_httponly_and_samesite(client):
    response = login(client)
    cookie = response.headers["Set-Cookie"]
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie


def test_seed_is_idempotent_and_dashboard_has_data(app, client):
    with app.app_context():
        assert seed_database() == 35
        assert seed_database() == 0
        assert db.session.scalar(db.select(db.func.count(Admin.id))) == 1
        records = db.session.scalars(db.select(PasswordCheck)).all()
        assert len(records) == 35
        assert len({record.created_at.date() for record in records}) >= 7
        assert len({record.strength for record in records}) == 5
    login(client)
    response = client.get("/admin/dashboard")
    assert response.status_code == 200
    assert "Showing 1–10 of 35" in response.text
    assert "distribution-chart" in response.text
    stats = client.get("/admin/stats").json
    assert stats["total"] == 35 and sum(stats["counts"]) == 35
    assert len(stats["daily_counts"]) == 7
    assert "Showing 11–20 of 35" in client.get("/admin/dashboard?page=2").text
