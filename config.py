"""Environment-based application settings."""
import os
import secrets
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///password_checker.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = os.getenv("APP_ENV", "development") != "production"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    MAX_CONTENT_LENGTH = 16 * 1024
    WTF_CSRF_TIME_LIMIT = 3600
