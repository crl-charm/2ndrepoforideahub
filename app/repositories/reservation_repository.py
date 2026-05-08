from __future__ import annotations

from datetime import date, time
from typing import Optional

from app import db
from app.models.reservation import Reservation


class ReservationRepository:
    def get(self, res_id: int) -> Optional[Reservation]:
        return Reservation.query.filter_by(id=res_id).first()

    def list_all(self) -> list[Reservation]:
        return Reservation.query.order_by(Reservation.reserved_date.desc()).all()

    def list_by_date(self, reserved_date: date) -> list[Reservation]:
        return Reservation.query.filter_by(reserved_date=reserved_date).order_by(
            Reservation.reserved_time
        ).all()

    def list_by_status(self, status: str) -> list[Reservation]:
        return Reservation.query.filter_by(status=status).order_by(
            Reservation.reserved_date
        ).all()

    def create(
        self,
        customer_name: str,
        customer_contact: str,
        space_type_id: int,
        reserved_date: date,
        reserved_time: time,
        duration_minutes: int,
        number_of_people: int,
        notes: Optional[str],
    ) -> Reservation:
        res = Reservation(
            customer_name=customer_name,
            customer_contact=customer_contact,
            space_type_id=space_type_id,
            reserved_date=reserved_date,
            reserved_time=reserved_time,
            duration_minutes=duration_minutes,
            number_of_people=number_of_people,
            notes=notes,
        )
        db.session.add(res)
        db.session.flush()
        return res

    def update_status(self, res_id: int, status: str) -> bool:
        res = self.get(res_id)
        if not res:
            return False
        res.status = status
        return True

    def delete(self, res_id: int) -> bool:
        res = self.get(res_id)
        if not res:
            return False
        db.session.delete(res)
        return True

    def save(self) -> None:
        db.session.commit()
