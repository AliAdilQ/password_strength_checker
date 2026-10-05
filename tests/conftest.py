import re
import pytest

from app import create_app
from app.extensions import db
from app.models import Admin


@pytest.fixture
def app(tmp_path):
    application = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-key-never-used-outside-tests",
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
    })
    with application.app_context():
        account = Admin(username="admin", email="admin@example.com")
        account.set_password("Admin@12345")
        db.session.add(account)
        db.session.commit()
    yield application
    with application.app_context():
        db.session.remove()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


def csrf_token(client, path="/"):
    response = client.get(path)
    return re.search(r'<meta name="csrf-token" content="([^"]+)"', response.text).group(1)


def login(client):
    token = csrf_token(client, "/admin/login")
    return client.post("/admin/login", data={"username": "admin", "password": "Admin@12345", "csrf_token": token})
