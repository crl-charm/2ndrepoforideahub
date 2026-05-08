from __future__ import annotations

from flask import Blueprint, jsonify, request, render_template

from app.core import get_notifier
from app.repositories.inventory_repository import InventoryRepository
from app.services.inventory_service import InventoryService
from app.utils.auth import login_required, admin_required

inventory_bp = Blueprint("inventory", __name__, url_prefix="/admin/inventory")

_service = InventoryService(repo=InventoryRepository())


@inventory_bp.route("", methods=["GET"])
@admin_required
def list_items() -> str:
    items = _service.list_all()
    return render_template("admin/inventory.html", items=items)


@inventory_bp.route("/api/items", methods=["GET"])
@login_required
def api_list_items() -> tuple:
    items = _service.list_all()
    return jsonify({"success": True, "data": items}), 200


@inventory_bp.route("/api/items", methods=["POST"])
@admin_required
def api_create_item() -> tuple:
    data = request.get_json()
    result = _service.create(
        menu_item_id=data.get("menu_item_id"),
        stock_qty=int(data.get("stock_qty", 0)),
        low_stock_threshold=int(data.get("low_stock_threshold", 10)),
        unit=data.get("unit", "pieces"),
    )
    return jsonify(result), 201


@inventory_bp.route("/api/items/<int:item_id>/stock", methods=["PATCH"])
@admin_required
def api_update_stock(item_id: int) -> tuple:
    data = request.get_json()
    from flask import session

    result = _service.update_stock(
        item_id=item_id,
        new_qty=int(data.get("new_qty")),
        reason=data.get("reason", "Manual adjustment"),
        user_id=session.get("user_id"),
    )
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result), 200


@inventory_bp.route("/api/items/<int:item_id>/logs", methods=["GET"])
@login_required
def api_get_logs(item_id: int) -> tuple:
    logs = _service.get_logs(item_id)
    return jsonify({"success": True, "data": logs}), 200


@inventory_bp.route("/api/low-stock", methods=["GET"])
@login_required
def api_low_stock() -> tuple:
    items = _service.get_low_stock()
    return jsonify({"success": True, "data": items}), 200
