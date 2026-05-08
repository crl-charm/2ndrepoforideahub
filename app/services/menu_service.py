from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app import socketio
from app.repositories.menu_repository import MenuRepository


@dataclass(frozen=True)
class MenuService:
    repo: MenuRepository

    def list_all(self) -> list[dict[str, Any]]:
        items = self.repo.list_all()
        return [
            {
                "id": item.id,
                "name": item.name,
                "price": float(item.price),
                "category": item.category,
                "is_available": item.is_available,
            }
            for item in items
        ]

    def list_available(self) -> list[dict[str, Any]]:
        items = self.repo.list_available()
        return [
            {
                "id": item.id,
                "name": item.name,
                "price": float(item.price),
                "category": item.category,
            }
            for item in items
        ]

    def create(self, name: str, price: float, category: str) -> dict[str, Any]:
        item = self.repo.create(name, price, category)
        self.repo.save()
        socketio.emit("menu_item_created", {"id": item.id, "name": item.name})
        return {"success": True, "data": {"id": item.id}}

    def update(
        self, item_id: int, name: str, price: float, category: str
    ) -> dict[str, Any] | tuple[dict[str, Any], int]:
        success = self.repo.update(item_id, name, price, category)
        if not success:
            return {"error": "Menu item not found"}, 404
        self.repo.save()
        socketio.emit("menu_item_updated", {"id": item_id, "name": name})
        return {"success": True}

    def toggle_availability(
        self, item_id: int
    ) -> dict[str, Any] | tuple[dict[str, Any], int]:
        success = self.repo.toggle_availability(item_id)
        if not success:
            return {"error": "Menu item not found"}, 404
        self.repo.save()
        item = self.repo.get(item_id)
        socketio.emit(
            "menu_item_updated",
            {"id": item_id, "is_available": item.is_available},
        )
        return {"success": True, "is_available": item.is_available}

    def delete(self, item_id: int) -> dict[str, Any] | tuple[dict[str, Any], int]:
        success = self.repo.delete(item_id)
        if not success:
            return {"error": "Menu item not found"}, 404
        self.repo.save()
        socketio.emit("menu_item_deleted", {"id": item_id})
        return {"success": True}
