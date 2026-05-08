from __future__ import annotations

from flask import Blueprint, jsonify

from app.repositories.analytics_repository import AnalyticsRepository
from app.services.analytics_service import AnalyticsService
from app.utils.auth import login_required

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

_service = AnalyticsService(repo=AnalyticsRepository())


@analytics_bp.route("/daily-revenue", methods=["GET"])
@login_required
def daily_revenue() -> tuple:
    data = _service.daily_revenue(30)
    return jsonify(data), 200


@analytics_bp.route("/top-items", methods=["GET"])
@login_required
def top_items() -> tuple:
    data = _service.top_menu_items(10)
    return jsonify(data), 200


@analytics_bp.route("/space-utilization", methods=["GET"])
@login_required
def space_utilization() -> tuple:
    data = _service.space_utilization()
    return jsonify(data), 200


@analytics_bp.route("/peak-hours", methods=["GET"])
@login_required
def peak_hours() -> tuple:
    data = _service.peak_hours()
    return jsonify(data), 200
