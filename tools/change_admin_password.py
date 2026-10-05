"""Replace local demo credentials without putting a new password in shell history."""
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from app.extensions import db
from app.models import Admin


if __name__ == "__main__":
    with create_app().app_context():
        username = input("Admin username: ").strip()
        account = db.session.scalar(db.select(Admin).where(Admin.username == username))
        if not account:
            raise SystemExit("Admin account not found. Run the seed script for local setup.")
        password = getpass.getpass("New password (at least 12 characters): ")
        if len(password) < 12 or password != getpass.getpass("Confirm password: "):
            raise SystemExit("Passwords must match and contain at least 12 characters.")
        account.set_password(password)
        del password
        db.session.commit()
        print("Admin password updated. Rotate SECRET_KEY to invalidate existing sessions.")
