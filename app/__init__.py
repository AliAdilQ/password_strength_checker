"""Flask application factory."""
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_wtf.csrf import CSRFError

from app.extensions import csrf, db, login_manager


def create_app(test_config=None):
    load_dotenv()
    from config import Config

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    if os.getenv("APP_ENV") == "production" and not test_config:
        key = app.config["SECRET_KEY"]
        if not os.getenv("SECRET_KEY") or len(key) < 32 or key == "change-this-secret-key":
            raise RuntimeError("Production requires a random SECRET_KEY of at least 32 characters.")
        if not app.config["SESSION_COOKIE_SECURE"]:
            raise RuntimeError("Production requires SESSION_COOKIE_SECURE=true and HTTPS.")
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "admin.login"
    login_manager.login_message = "Sign in to access your analytics dashboard."
    login_manager.login_message_category = "info"

    from app.models import Admin

    @login_manager.user_loader
    def load_admin(admin_id):
        try:
            return db.session.get(Admin, int(admin_id))
        except (ValueError, TypeError):
            return None

    from app.routes.admin import admin
    from app.routes.api import api
    from app.routes.main import main
    app.register_blueprint(main)
    app.register_blueprint(api)
    app.register_blueprint(admin)

    @app.after_request
    def security_headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "font-src 'self'; img-src 'self' data:; connect-src 'self'; "
            "object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
        )
        return response

    @app.errorhandler(CSRFError)
    def handle_csrf(error):
        if request.path.startswith("/api/"):
            return jsonify(error="Your session expired. Refresh the page and try again."), 400
        return render_template("errors/error.html", code=400, title="Let's refresh that session.",
                               message="This form has expired. Reload the page and try again."), 400

    def error_page(code, title, message):
        if request.path.startswith("/api/"):
            return jsonify(error=message), code
        return render_template("errors/error.html", code=code, title=title, message=message), code

    @app.errorhandler(404)
    def not_found(error):
        return error_page(404, "This page is off the grid.", "The page you're looking for doesn't exist. Let's get you back to safety.")

    @app.errorhandler(403)
    def forbidden(error):
        return error_page(403, "A little extra protection.", "You don't have permission to access this page.")

    @app.errorhandler(413)
    def too_large(error):
        return error_page(413, "That's a little too much.", "The request exceeds the 16 KB limit.")

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return error_page(500, "We hit a small roadblock.", "Something went wrong. Please try again in a moment.")

    with app.app_context():
        db.create_all()
    return app
