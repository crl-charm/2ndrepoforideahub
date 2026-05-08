from __future__ import annotations

from flask import Blueprint, jsonify, request, render_template

from app.repositories.menu_repository import MenuRepository
from app.services.menu_service import MenuService
from app.utils.auth import admin_required, login_required

menu_bp = Blueprint("menu", __name__, url_prefix="/admin/menu")

_service = MenuService(repo=MenuRepository())


@menu_bp.route("", methods=["GET"])
@admin_required
def menu_page() -> str:
    items = _service.list_all()
    return render_template("admin/menu.html", items=items)


@menu_bp.route("/api/items", methods=["GET"])
@login_required
def api_list_items() -> tuple:
    items = _service.list_available()
    return jsonify({"success": True, "data": items}), 200


@menu_bp.route("/api/items/all", methods=["GET"])
@admin_required
def api_all_items() -> tuple:
    items = _service.list_all()
    return jsonify({"success": True, "data": items}), 200


@menu_bp.route("/api/items", methods=["POST"])
@admin_required
def api_create_item() -> tuple:
    data = request.get_json()
    result = _service.create(
        name=data.get("name"),
        price=float(data.get("price")),
        category=data.get("category"),
    )
    return jsonify(result), 201


@menu_bp.route("/api/items/<int:item_id>", methods=["PATCH"])
@admin_required
def api_update_item(item_id: int) -> tuple:
    data = request.get_json()
    result = _service.update(
        item_id=item_id,
        name=data.get("name"),
        price=float(data.get("price")),
        category=data.get("category"),
    )
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result), 200


@menu_bp.route("/api/items/<int:item_id>/availability", methods=["PATCH"])
@admin_required
def api_toggle_availability(item_id: int) -> tuple:
    result = _service.toggle_availability(item_id)
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result), 200


@menu_bp.route("/api/items/<int:item_id>", methods=["DELETE"])
@admin_required
def api_delete_item(item_id: int) -> tuple:
    result = _service.delete(item_id)
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result), 200
