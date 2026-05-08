from __future__ import annotations

from flask import Blueprint, jsonify, request, render_template, url_for

from app.repositories.qr_repository import QRRepository
from app.services.qr_service import QRService
from app.utils.auth import admin_required, login_required
from app.repositories.menu_repository import MenuRepository
from app.services.menu_service import MenuService

qr_bp = Blueprint("qr", __name__, url_prefix="/qr")
order_bp = Blueprint("self_order", __name__, url_prefix="/order")

_qr_service = QRService(repo=QRRepository())
_menu_service = MenuService(repo=MenuRepository())


@qr_bp.route("/generate/<int:space_id>", methods=["POST"])
@admin_required
def generate_qr(space_id: int) -> tuple:
    base_url = request.host_url.rstrip("/")
    result = _qr_service.get_space_qr(space_id, base_url)
    return jsonify(result), 201


@qr_bp.route("/spaces", methods=["GET"])
@admin_required
def list_space_qrs() -> tuple:
    base_url = request.host_url.rstrip("/")
    from app.repositories.session_repository import SessionRepository

    repo = SessionRepository()
    spaces = repo.get_all_spaces()
    qr_data = []
    for space in spaces:
        if hasattr(space, "qr_token") and space.qr_token:
            qr_code = _qr_service.repo.generate_qr_code(space.qr_token, base_url)
            qr_data.append({
                "space_id": space.id,
                "space_name": space.name,
                "token": space.qr_token,
                "qr_code": qr_code,
            })
    return jsonify({"success": True, "data": qr_data}), 200


@order_bp.route("/<token>", methods=["GET"])
def order_page(token: str) -> str:
    result = _qr_service.get_space_by_token(token)
    if isinstance(result, tuple):
        return render_template("error.html", message="Invalid QR code"), 404

    space_info = result["data"]
    menu_items = _menu_service.list_available()
    return render_template(
        "self_order.html",
        token=token,
        space_id=space_info["space_id"],
        space_name=space_info["space_name"],
        menu_items=menu_items,
    )


@order_bp.route("/<token>/submit", methods=["POST"])
def submit_order(token: str) -> tuple:
    result = _qr_service.get_space_by_token(token)
    if isinstance(result, tuple):
        return jsonify({"error": "Invalid QR code"}), 404

    data = request.get_json()
    space_id = result["data"]["space_id"]

    from app.services.order_service import OrderService
    from app.repositories.order_repository import OrderRepository

    order_service = OrderService(repo=OrderRepository())
    order_data = {
        "customer_name": data.get("customer_name", "Walk-in"),
        "space_type_id": space_id,
        "items": data.get("items", []),
    }
    order_result = order_service.create_from_qr(order_data)
    return jsonify(order_result), 201 if order_result.get("success") else 400
