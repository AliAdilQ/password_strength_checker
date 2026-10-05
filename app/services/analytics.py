"""Aggregate safe metadata for the dashboard."""
from datetime import timedelta

from sqlalchemy import func

from app.extensions import db
from app.models import PasswordCheck, utc_now
from app.services.password_analyzer import CATEGORIES


def dashboard_stats():
    today = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
    count, score, length = db.session.execute(db.select(
        func.count(PasswordCheck.id), func.avg(PasswordCheck.score), func.avg(PasswordCheck.password_length)
    )).one()
    grouped = dict(db.session.execute(db.select(PasswordCheck.strength, func.count(PasswordCheck.id))
                                     .group_by(PasswordCheck.strength)).all())
    daily = dict(db.session.execute(db.select(func.date(PasswordCheck.created_at), func.count(PasswordCheck.id))
                                   .where(PasswordCheck.created_at >= today - timedelta(days=6))
                                   .group_by(func.date(PasswordCheck.created_at))).all())
    dates = [today - timedelta(days=day) for day in range(6, -1, -1)]
    checks_today = db.session.scalar(db.select(func.count(PasswordCheck.id)).where(PasswordCheck.created_at >= today))
    return {
        "total": count, "average_score": round(score or 0, 1), "average_length": round(length or 0, 1),
        "today": checks_today, "categories": CATEGORIES, "counts": [grouped.get(name, 0) for name in CATEGORIES],
        "dates": [day.strftime("%b %d") for day in dates],
        "daily_counts": [daily.get(day.strftime("%Y-%m-%d"), 0) for day in dates],
    }
