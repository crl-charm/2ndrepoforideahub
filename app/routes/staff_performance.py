from __future__ import annotations

from flask import Blueprint, jsonify, request, render_template

from app.repositories.staff_repository import StaffRepository
from app.services.staff_performance_service import StaffPerformanceService
from app.utils.auth import admin_required, login_required

staff_performance_bp = Blueprint(
    "staff_performance", __name__, url_prefix="/admin/staff-performance"
)

_service = StaffPerformanceService(repo=StaffRepository())


@staff_performance_bp.route("", methods=["GET"])
@admin_required
def leaderboard() -> str:
    logs = _service.list_all()
    return render_template("admin/staff_performance.html", logs=logs)


@staff_performance_bp.route("/api/logs", methods=["GET"])
@login_required
def api_list_logs() -> tuple:
    logs = _service.list_all()
    return jsonify({"success": True, "data": logs}), 200


@staff_performance_bp.route("/api/logs", methods=["POST"])
@admin_required
def api_create_log() -> tuple:
    data = request.get_json()
    result = _service.create(
        user_id=data.get("user_id"),
        shift_date=data.get("shift_date"),
        orders_handled=int(data.get("orders_handled", 0)),
        avg_order_minutes=float(data.get("avg_order_minutes", 0)),
        sessions_managed=int(data.get("sessions_managed", 0)),
        upsell_count=int(data.get("upsell_count", 0)),
        admin_note=data.get("admin_note"),
    )
    return jsonify(result), 201


@staff_performance_bp.route("/api/logs/by-date/<date_str>", methods=["GET"])
@login_required
def api_by_date(date_str: str) -> tuple:
    logs = _service.list_by_date(date_str)
    return jsonify({"success": True, "data": logs}), 200


@staff_performance_bp.route("/api/logs/by-user/<int:user_id>", methods=["GET"])
@login_required
def api_by_user(user_id: int) -> tuple:
    logs = _service.list_by_user(user_id)
    return jsonify({"success": True, "data": logs}), 200
