from functools import wraps
from flask import session, redirect, jsonify, flash, request


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized"}), 401
            flash("Please log in first!", "danger")
            return redirect("/login")
        return view_func(*args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized"}), 401
            flash("Please log in first!", "danger")
            return redirect("/login")
        if session.get("job_role") not in {"admin", "manager"}:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Forbidden"}), 403
            flash("Admin access required.", "danger")
            return redirect("/dashboard")
        return view_func(*args, **kwargs)
    return wrapper