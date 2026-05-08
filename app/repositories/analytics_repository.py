from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Any

from sqlalchemy import func

from app import db
from app.models import Transaction, Order, CustomerSession, MenuItem


class AnalyticsRepository:
    def daily_revenue(self, days: int = 30) -> list[dict[str, Any]]:
        start_date = date.today() - timedelta(days=days)
        result = (
            db.session.query(
                func.date(Transaction.created_at).label("date"),
                func.sum(Transaction.total_bill).label("revenue"),
            )
            .filter(func.date(Transaction.created_at) >= start_date)
            .group_by(func.date(Transaction.created_at))
            .order_by(func.date(Transaction.created_at))
            .all()
        )
        return [
            {
                "date": str(row.date),
                "revenue": float(row.revenue or 0),
            }
            for row in result
        ]

    def top_menu_items(self, limit: int = 10) -> list[dict[str, Any]]:
        result = (
            db.session.query(
                MenuItem.name,
                func.count(MenuItem.id).label("count"),
                func.sum(MenuItem.price).label("total"),
            )
            .join(MenuItem)
            .group_by(MenuItem.id)
            .order_by(func.count(MenuItem.id).desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "name": row.name,
                "count": int(row.count),
                "total": float(row.total or 0),
            }
            for row in result
        ]

    def space_utilization(self) -> list[dict[str, Any]]:
        result = (
            db.session.query(
                CustomerSession.space_type_id,
            )
            .group_by(CustomerSession.space_type_id)
            .all()
        )
        return [{"space_id": row.space_type_id} for row in result]

    def peak_hours(self) -> list[dict[str, Any]]:
        result = (
            db.session.query(
                func.hour(Transaction.created_at).label("hour"),
                func.count(Transaction.id).label("count"),
            )
            .filter(Transaction.created_at.isnot(None))
            .group_by(func.hour(Transaction.created_at))
            .order_by(func.hour(Transaction.created_at))
            .all()
        )
        return [
            {
                "hour": int(row.hour or 0),
                "count": int(row.count),
            }
            for row in result
        ]
