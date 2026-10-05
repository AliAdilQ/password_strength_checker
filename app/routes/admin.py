"""CSRF-protected administrator authentication and safe analytics."""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import Admin, PasswordCheck
from app.services.analytics import dashboard_stats

admin = Blueprint("admin", __name__, url_prefix="/admin")
_DUMMY_HASH = generate_password_hash("timing-equalization-placeholder", method="scrypt")


@admin.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()[:80]
        password = request.form.get("password", "")
        account = db.session.scalar(db.select(Admin).where(Admin.username == username))
        valid = check_password_hash(account.password_hash if account else _DUMMY_HASH, password)
        del password
        if account and valid:
            session.clear()
            session.permanent = True
            login_user(account)
            return redirect(url_for("admin.dashboard"))
        flash("The username or password is incorrect. Please try again.", "error")
        return render_template("admin/login.html"), 401
    return render_template("admin/login.html")


@admin.get("/dashboard")
@login_required
def dashboard():
    page = request.args.get("page", 1, type=int)
    records = db.paginate(db.select(PasswordCheck).order_by(PasswordCheck.created_at.desc(), PasswordCheck.id.desc()),
                          page=max(1, page), per_page=10, error_out=False)
    return render_template("admin/dashboard.html", stats=dashboard_stats(), records=records)


@admin.get("/stats")
@login_required
def stats():
    return dashboard_stats()


@admin.post("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been signed out securely.", "success")
    return redirect(url_for("admin.login"))
