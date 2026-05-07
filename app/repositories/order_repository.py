from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import func

from app import db
from app.models import CustomerSession, MenuItem, Order, OrderItem


@dataclass(frozen=True)
class OrderRepository:
    def list_menu_items(self) -> list[MenuItem]:
        return MenuItem.query.all()

    def get_session(self, session_id: int) -> Optional[CustomerSession]:
        return CustomerSession.query.get(session_id)

    def get_order(self, order_id: int) -> Optional[Order]:
        return Order.query.get(order_id)

    def get_order_item(self, item_id: int) -> Optional[OrderItem]:
        return OrderItem.query.get(item_id)

    def add_order_with_items(self, session_id: int, handled_by: Optional[int], items: list[dict]) -> int:
        new_order = Order(customer_session_id=session_id, status="preparing", handled_by=handled_by)
        db.session.add(new_order)
        db.session.commit()

        for item in items:
            menu_item_id = item.get("menu_item_id")
            if not menu_item_id:
                continue
            menu_item = MenuItem.query.get(menu_item_id)
            if not menu_item:
                continue

            order_item = OrderItem(
                order_id=new_order.id,
                menu_item_id=menu_item.id,
                quantity=item.get("quantity", 1),
                price=menu_item.price,
            )
            db.session.add(order_item)

        db.session.commit()
        return int(new_order.id)

    def list_orders_for_session(self, session_id: int, include_done: bool) -> list[Order]:
        q = Order.query.filter_by(customer_session_id=session_id)
        if not include_done:
            q = q.filter(Order.status != "done")
        return q.all()

    def pending_counts(self) -> dict[str, int]:
        pending_sessions = (
            db.session.query(func.count(func.distinct(Order.customer_session_id)))
            .join(CustomerSession, CustomerSession.id == Order.customer_session_id)
            .filter(CustomerSession.status == "active")
            .filter(Order.status != "done")
            .scalar()
        ) or 0

        pending_items = (
            db.session.query(func.coalesce(func.sum(OrderItem.quantity), 0))
            .select_from(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .join(CustomerSession, CustomerSession.id == Order.customer_session_id)
            .filter(CustomerSession.status == "active")
            .filter(Order.status != "done")
            .scalar()
        ) or 0

        return {"pending_sessions": int(pending_sessions), "pending_items": int(pending_items)}

    def commit(self) -> None:
        db.session.commit()

