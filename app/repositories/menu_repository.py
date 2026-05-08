from __future__ import annotations

from typing import Optional
from app import db
from app.models.menu_item import MenuItem


class MenuRepository:
    def get(self, item_id: int) -> Optional[MenuItem]:
        return MenuItem.query.filter_by(id=item_id).first()

    def list_all(self) -> list[MenuItem]:
        return MenuItem.query.order_by(MenuItem.name).all()

    def list_available(self) -> list[MenuItem]:
        return MenuItem.query.filter_by(is_available=True).order_by(MenuItem.name).all()

    def create(self, name: str, price: float, category: str) -> MenuItem:
        item = MenuItem(name=name, price=price, category=category, is_available=True)
        db.session.add(item)
        db.session.flush()
        return item

    def update(self, item_id: int, name: str, price: float, category: str) -> bool:
        item = self.get(item_id)
        if not item:
            return False
        item.name = name
        item.price = price
        item.category = category
        return True

    def toggle_availability(self, item_id: int) -> bool:
        item = self.get(item_id)
        if not item:
            return False
        item.is_available = not item.is_available
        return True

    def delete(self, item_id: int) -> bool:
        item = self.get(item_id)
        if not item:
            return False
        db.session.delete(item)
        return True

    def save(self) -> None:
        db.session.commit()
