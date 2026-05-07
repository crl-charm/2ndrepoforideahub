from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from app.utils.auth import login_required

from app import socketio
from app.core.clock import SystemClock
from app.core.notifier import SocketIONotifier
from app.repositories.session_repository import SessionRepository
from app.services.session_service import SessionService


# Blueprint groups related routes together
session_bp = Blueprint("session_routes", __name__)

_service = SessionService(
    repo=SessionRepository(),
    clock=SystemClock(),
    notifier=SocketIONotifier(socketio=socketio),
)


# -----------------------------
# CHECK-IN CUSTOMER
# -----------------------------
@session_bp.route("/api/checkin", methods=["POST"])
#@login_required
def checkin():

    data = request.get_json()
    payload, status = _service.checkin(
        customer_name=data.get("customer_name"),
        school=data.get("school"),
        course=data.get("course"),
        space_type_id=data.get("space_type_id"),
        number_of_people=int(data.get("number_of_people", 1) or 1),
    )
    return jsonify(payload), status


# -----------------------------
# GET ACTIVE SESSIONS
# (LIVE RUNNING BILL)
# -----------------------------
@session_bp.route("/api/active-sessions")
@login_required
def get_active_sessions():
    return jsonify(_service.get_active_sessions_view())


# -----------------------------
# CHECKOUT CUSTOMER
# -----------------------------
@session_bp.route("/api/checkout/<int:session_id>", methods=["POST"])
@login_required
def checkout(session_id):
    resp = _service.checkout(session_id)
    if isinstance(resp, tuple):
        payload, status = resp
        return jsonify(payload), status
    return jsonify(resp)

@session_bp.route("/api/preview-checkout/<int:session_id>")
def preview_checkout(session_id):
    resp = _service.preview_checkout(session_id)
    if isinstance(resp, tuple):
        payload, status = resp
        return jsonify(payload), status
    return jsonify(resp)


@session_bp.route("/api/checkout-records")
@login_required
def checkout_records():
    transactions = _service.checkout_records()

    # Optional date-range filter (YYYY-MM-DD strings from the frontend)
    date_from_str = request.args.get("date_from", "").strip()
    date_to_str   = request.args.get("date_to",   "").strip()

    date_from = None
    date_to   = None
    try:
        if date_from_str:
            date_from = datetime.strptime(date_from_str, "%Y-%m-%d").date()
        if date_to_str:
            date_to = datetime.strptime(date_to_str, "%Y-%m-%d").date()
    except ValueError:
        pass  # Ignore bad dates — return unfiltered

    result = []

    for tx in transactions:
        sess = tx.session

        # Apply date filter on created_at (UTC date is fine for grouping purposes)
        if date_from and tx.created_at.date() < date_from:
            continue
        if date_to and tx.created_at.date() > date_to:
            continue

        time_in_text = (sess.time_in + timedelta(hours=8)).strftime("%B %d, %Y %I:%M %p") if sess and sess.time_in else "N/A"
        time_out_text = (sess.time_out + timedelta(hours=8)).strftime("%B %d, %Y %I:%M %p") if sess and sess.time_out else "N/A"

        seconds_spent = int((sess.time_out - sess.time_in).total_seconds()) if sess and sess.time_in and sess.time_out else None
        minutes_spent = round(seconds_spent / 60, 2) if seconds_spent is not None else None

        result.append({
            "transaction_id": tx.id,
            "customer_name": sess.customer_name if sess else "N/A",
            "space_type": sess.space_type.name if sess and sess.space_type else "N/A",
            "time_in": time_in_text,
            "time_out": time_out_text,
            "time_bill": float(tx.time_bill),
            "food_bill": float(tx.food_bill),
            "total_bill": float(tx.total_bill),
            "seconds_spent": seconds_spent,
            "minutes_spent": minutes_spent,
            "created_date": tx.created_at.strftime("%Y-%m-%d")
        })

    return jsonify(result)


@session_bp.route("/api/space-availability")
@login_required
def space_availability():
    return jsonify(_service.space_availability())