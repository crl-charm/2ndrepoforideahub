from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Any, Optional

from app.repositories.reservation_repository import ReservationRepository


@dataclass(frozen=True)
class ReservationService:
    repo: ReservationRepository

    def list_all(self) -> list[dict[str, Any]]:
        reservations = self.repo.list_all()
        return [
            {
                "id": r.id,
                "customer_name": r.customer_name,
                "customer_contact": r.customer_contact,
                "space": r.space_type.name if r.space_type else "Unknown",
                "reserved_date": r.reserved_date.strftime("%Y-%m-%d"),
                "reserved_time": r.reserved_time.strftime("%H:%M"),
                "duration_minutes": r.duration_minutes,
                "number_of_people": r.number_of_people,
                "status": r.status,
                "notes": r.notes,
            }
            for r in reservations
        ]

    def list_by_status(self, status: str) -> list[dict[str, Any]]:
        reservations = self.repo.list_by_status(status)
        return [
            {
                "id": r.id,
                "customer_name": r.customer_name,
                "space": r.space_type.name if r.space_type else "Unknown",
                "reserved_date": r.reserved_date.strftime("%Y-%m-%d"),
                "reserved_time": r.reserved_time.strftime("%H:%M"),
            }
            for r in reservations
        ]

    def create(
        self,
        customer_name: str,
        customer_contact: str,
        space_type_id: int,
        reserved_date: str,
        reserved_time: str,
        duration_minutes: int,
        number_of_people: int,
        notes: Optional[str],
    ) -> dict[str, Any]:
        date_obj = date.fromisoformat(reserved_date)
        time_obj = time.fromisoformat(reserved_time)
        res = self.repo.create(
            customer_name,
            customer_contact,
            space_type_id,
            date_obj,
            time_obj,
            duration_minutes,
            number_of_people,
            notes,
        )
        self.repo.save()
        return {"success": True, "data": {"id": res.id}}

    def update_status(
        self, res_id: int, status: str
    ) -> dict[str, Any] | tuple[dict[str, Any], int]:
        success = self.repo.update_status(res_id, status)
        if not success:
            return {"error": "Reservation not found"}, 404
        self.repo.save()
        return {"success": True}

    def delete(self, res_id: int) -> dict[str, Any] | tuple[dict[str, Any], int]:
        success = self.repo.delete(res_id)
        if not success:
            return {"error": "Reservation not found"}, 404
        self.repo.save()
        return {"success": True}
