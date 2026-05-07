from flask import Blueprint, jsonify, request, render_template, session as flask_session
from decimal import Decimal
from datetime import timedelta
from app.utils.auth import login_required

from app import db
from app.models import Order, OrderItem, CustomerSession
from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService


# Blueprint for order related routes
order_bp = Blueprint("order_routes", __name__)

_service = OrderService(repo=OrderRepository())


# ----------------------------------
# GET MENU ITEMS
# ----------------------------------
@order_bp.route("/api/menu")
@login_required
def get_menu():
    return jsonify(_service.list_menu())


# ----------------------------------
# ADD ORDER
# ----------------------------------
@order_bp.route("/api/add-order", methods=["POST"])
@login_required
def add_order():

    data = request.get_json()

    session_id = data.get("session_id")
    items = data.get("items")

    if not session_id or not items:
        return jsonify({"error": "session_id and items are required"}), 400
    handled_by = flask_session.get("user_id")
    resp = _service.add_order(session_id=int(session_id), items=items, handled_by=handled_by)
    if isinstance(resp, tuple):
        payload, status = resp
        return jsonify(payload), status
    return jsonify(resp)


# ----------------------------------
# UPDATE ORDER STATUS (preparing -> serving)
# ----------------------------------
@order_bp.route("/api/order-status/<int:order_id>", methods=["PUT"])
@login_required
def update_order_status(order_id):
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    resp = _service.update_order_status(order_id=order_id, new_status=new_status)
    if isinstance(resp, tuple):
        payload, status = resp
        return jsonify(payload), status
    return jsonify(resp)


# ----------------------------------
# GET SESSION ORDERS
# ----------------------------------
@order_bp.route("/api/session-orders/<int:session_id>")
@login_required
def get_session_orders(session_id):
    # By default, hide completed orders ("done") from the customer orders page.
    # The dashboard receipt needs them, so it can call with `?include_done=1`.
    include_done = request.args.get("include_done", "0").lower() in {"1", "true", "yes"}
    return jsonify(_service.get_session_orders(session_id=session_id, include_done=include_done))


@order_bp.route("/order/<int:session_id>")
@login_required
def order_page(session_id):
    return render_template("order.html", session_id=session_id)


# ----------------------------------
# ORDERS (VIEW ONLY)
# ----------------------------------
@order_bp.route("/orders")
@login_required
def orders_list_page():
    return render_template("orders_list.html")


@order_bp.route("/api/orders-list")
@login_required
def orders_list_api():
    sessions = CustomerSession.query.filter_by(status="active").order_by(CustomerSession.time_in.desc()).all()
    result = []

    for sess in sessions:
        # Hide completed orders.
        orders = Order.query.filter_by(customer_session_id=sess.id).filter(Order.status != "done").all()
        if not orders:
            continue

        item_count = 0
        food_total = Decimal("0.00")

        for order in orders:
            for item in order.items:
                food_total += item.quantity * item.price
                item_count += 1

        latest_order = (
            Order.query
            .filter_by(customer_session_id=sess.id)
            .filter(Order.status != "done")
            .order_by(Order.id.desc())
            .first()
        )
        latest_status = latest_order.status if latest_order else "preparing"
        if latest_status == "preparin":
            latest_status = "preparing"

        time_in_text = (sess.time_in + timedelta(hours=8)).strftime("%B %d, %Y %I:%M %p") if sess.time_in else "N/A"

        result.append({
            "session_id": sess.id,
            "customer_name": sess.customer_name,
            "space_type": sess.space_type.name if sess.space_type else "N/A",
            "time_in": time_in_text,
            "orders_count": item_count,
            "food_total": float(food_total),
            "active_order_status": latest_status
        })

    return jsonify(result)


@order_bp.route("/api/orders/pending-count")
@login_required
def orders_pending_count():
    return jsonify(_service.pending_count())


@order_bp.route("/orders/<int:session_id>")
@login_required
def orders_view_page(session_id):
    return render_template("orders_view.html", session_id=session_id)


@order_bp.route("/api/void-item/<int:item_id>", methods=["DELETE"])
@login_required
def void_item(item_id):

    item = OrderItem.query.get(item_id)

    if not item:
        return jsonify({"error": "Item not found"}), 404

    if item.quantity > 1:
        item.quantity -= 1
    else:
        db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "One item voided successfully"})


# ----------------------------------
# TOGGLE ORDER ITEM STATUS (preparing <-> done)
# ----------------------------------
@order_bp.route("/api/order-item-status/<int:item_id>", methods=["PUT"])
@login_required
def toggle_order_item_status(item_id):
    item = OrderItem.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    # Toggle between preparing and done
    if item.status in {"preparing", "preparin", None}:
        item.status = "done"
    else:
        item.status = "preparing"

    db.session.commit()
    return jsonify({"message": "Item status updated", "item_id": item_id, "status": item.status})


# ----------------------------------
# MARK ALL SESSION ORDERS AS SERVED
# ----------------------------------
@order_bp.route("/api/session-served/<int:session_id>", methods=["POST"])
@login_required
def session_served(session_id):
    sess = CustomerSession.query.get(session_id)
    if not sess:
        return jsonify({"error": "Session not found"}), 404

    if sess.status != "active":
        return jsonify({"error": "Session is not active"}), 400

    orders = Order.query.filter_by(customer_session_id=session_id).filter(Order.status != "done").all()
    for order in orders:
        order.status = "done"
        for item in order.items:
            item.status = "done"

    db.session.commit()
    return jsonify({"message": "Session marked as served", "session_id": session_id})

