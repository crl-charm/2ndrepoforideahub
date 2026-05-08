from __future__ import annotations

from flask import Blueprint, jsonify, request, render_template, session

from app.repositories.receivable_repository import ReceivableRepository
from app.services.receivable_service import ReceivableService
from app.utils.auth import admin_required, login_required

receivables_bp = Blueprint("receivables", __name__, url_prefix="/admin/receivables")

_service = ReceivableService(repo=ReceivableRepository())


@receivables_bp.route("", methods=["GET"])
@admin_required
def list_receivables() -> str:
    receivables = _service.list_all()
    return render_template("admin/receivables.html", receivables=receivables)


@receivables_bp.route("/api/receivables", methods=["GET"])
@login_required
def api_list_receivables() -> tuple:
    receivables = _service.list_all()
    return jsonify({"success": True, "data": receivables}), 200


@receivables_bp.route("/api/receivables", methods=["POST"])
@admin_required
def api_create_receivable() -> tuple:
    data = request.get_json()
    result = _service.create(
        customer_name=data.get("customer_name"),
        customer_contact=data.get("customer_contact"),
        items_description=data.get("items_description"),
        amount_owed=float(data.get("amount_owed")),
        due_date=data.get("due_date"),
        created_by=session.get("user_id"),
        session_id=data.get("session_id"),
    )
    return jsonify(result), 201


@receivables_bp.route("/api/receivables/<int:rec_id>/mark-paid", methods=["PATCH"])
@admin_required
def api_mark_paid(rec_id: int) -> tuple:
    result = _service.mark_paid(rec_id)
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result), 200


@receivables_bp.route("/api/receivables/unpaid", methods=["GET"])
@login_required
def api_unpaid() -> tuple:
    receivables = _service.list_unpaid()
    return jsonify({"success": True, "data": receivables}), 200
