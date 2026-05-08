from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Optional

from app.repositories.staff_repository import StaffRepository


@dataclass(frozen=True)
class StaffPerformanceService:
    repo: StaffRepository

    def list_all(self) -> list[dict[str, Any]]:
        logs = self.repo.list_all()
        return [
            {
                "id": log.id,
                "user_id": log.user_id,
                "username": log.user.username if log.user else "Unknown",
                "shift_date": log.shift_date.strftime("%Y-%m-%d"),
                "orders_handled": log.orders_handled,
                "avg_order_minutes": float(log.avg_order_minutes),
                "sessions_managed": log.sessions_managed,
                "upsell_count": log.upsell_count,
                "score": float(log.score),
                "admin_note": log.admin_note,
            }
            for log in logs
        ]

    def list_by_date(self, shift_date: str) -> list[dict[str, Any]]:
        date_obj = date.fromisoformat(shift_date)
        logs = self.repo.list_by_date(date_obj)
        return [
            {
                "id": log.id,
                "username": log.user.username,
                "orders_handled": log.orders_handled,
                "sessions_managed": log.sessions_managed,
                "upsell_count": log.upsell_count,
                "score": float(log.score),
            }
            for log in logs
        ]

    def list_by_user(self, user_id: int) -> list[dict[str, Any]]:
        logs = self.repo.list_by_user(user_id)
        return [
            {
                "id": log.id,
                "shift_date": log.shift_date.strftime("%Y-%m-%d"),
                "orders_handled": log.orders_handled,
                "sessions_managed": log.sessions_managed,
                "score": float(log.score),
            }
            for log in logs
        ]

    def create(
        self,
        user_id: int,
        shift_date: str,
        orders_handled: int,
        avg_order_minutes: float,
        sessions_managed: int,
        upsell_count: int,
        admin_note: Optional[str],
    ) -> dict[str, Any]:
        date_obj = date.fromisoformat(shift_date)
        log = self.repo.create(
            user_id,
            date_obj,
            orders_handled,
            Decimal(str(avg_order_minutes)),
            sessions_managed,
            upsell_count,
            admin_note,
        )
        self.repo.save()
        return {"success": True, "data": {"id": log.id, "score": float(log.score)}}
