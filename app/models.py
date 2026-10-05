"""Only administrator credentials are hashed; checker inputs have no storage field."""
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="scrypt")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class PasswordCheck(db.Model):
    __table_args__ = (
        db.CheckConstraint("score BETWEEN 0 AND 100", name="valid_score"),
        db.CheckConstraint("password_length BETWEEN 1 AND 256", name="valid_length"),
    )
    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    password_length = db.Column(db.Integer, nullable=False)
    has_uppercase = db.Column(db.Boolean, nullable=False)
    has_lowercase = db.Column(db.Boolean, nullable=False)
    has_number = db.Column(db.Boolean, nullable=False)
    has_symbol = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now, index=True)
