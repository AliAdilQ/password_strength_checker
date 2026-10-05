"""Idempotent local-demo seed: credentials are hashed, analytics are metadata only."""
from datetime import timedelta

from app import create_app
from app.extensions import db
from app.models import Admin, PasswordCheck, utc_now
from app.services.password_analyzer import strength_for_score


def seed_database():
    db.create_all()
    if not db.session.scalar(db.select(Admin).where(Admin.username == "admin")):
        account = Admin(username="admin", email="admin@example.com")
        account.set_password("Admin@12345")
        db.session.add(account)
    added = 0
    if not db.session.scalar(db.select(PasswordCheck.id).limit(1)):
        scores = [8, 18, 22, 28, 36, 42, 48, 53, 62, 67, 74, 81, 86, 93, 100,
                  12, 34, 55, 77, 95, 16, 39, 58, 82, 98, 21, 43, 64, 84, 96,
                  9, 31, 51, 71, 91]
        now = utc_now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elapsed_seconds = max(1, int((now - today).total_seconds()))
        day_offsets = [0] * 7 + [1] * 4 + [2] * 8 + [3] * 3 + [4] * 5 + [5] * 6 + [6] * 2
        for index, score in enumerate(scores):
            db.session.add(PasswordCheck(
                strength=strength_for_score(score), score=score,
                password_length=5 + score // 7, has_uppercase=score >= 35,
                has_lowercase=index % 5 != 0, has_number=index % 4 != 0,
                has_symbol=score >= 60,
                created_at=today - timedelta(days=day_offsets[index]) + timedelta(seconds=(index * 1793) % elapsed_seconds),
            ))
        added = len(scores)
    db.session.commit()
    return added


if __name__ == "__main__":
    with create_app().app_context():
        added = seed_database()
        print(f"Database ready. Demo admin available; {added} analytics records added.")
