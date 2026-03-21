"""
admin.py - Admin Blueprint
===========================
Admin-only routes: dashboard, user management, summary oversight.
"""

import logging
from functools import wraps
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, abort
)
from flask_login import login_required, current_user
from models import db, User, Summary

logger = logging.getLogger(__name__)
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ── Access guard ──────────────────────────────────────────────────────────────

def admin_required(f):
    """Decorator: only allow access to users with is_admin=True."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return login_required(decorated)


# ── Dashboard ─────────────────────────────────────────────────────────────────

@admin_bp.route("/")
@admin_required
def dashboard():
    users     = User.query.order_by(User.created_at.desc()).all()
    summaries = Summary.query.order_by(Summary.created_at.desc()).all()

    stats = {
        "total_users":     User.query.count(),
        "total_summaries": Summary.query.count(),
        "admin_count":     User.query.filter_by(is_admin=True).count(),
        "active_users":    User.query.filter_by(is_active=True).count(),
    }

    return render_template(
        "admin_dashboard.html",
        users=users,
        summaries=summaries,
        stats=stats,
    )


# ── User management ───────────────────────────────────────────────────────────

@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@admin_required
def toggle_user(user_id: int):
    """Activate or deactivate a user account."""
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash("Cannot deactivate another admin account.", "warning")
        return redirect(url_for("admin.dashboard"))

    user.is_active = not user.is_active
    db.session.commit()
    state = "activated" if user.is_active else "deactivated"
    flash(f"User '{user.username}' has been {state}.", "success")
    logger.info("Admin %s %s user %s", current_user.username, state, user.username)
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id: int):
    """Permanently delete a user and all their summaries."""
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash("Cannot delete an admin account.", "danger")
        return redirect(url_for("admin.dashboard"))

    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f"User '{username}' and all their data have been deleted.", "success")
    logger.info("Admin %s deleted user %s", current_user.username, username)
    return redirect(url_for("admin.dashboard"))


# ── Summary management ────────────────────────────────────────────────────────

@admin_bp.route("/summaries/<int:summary_id>/delete", methods=["POST"])
@admin_required
def delete_summary(summary_id: int):
    """Delete a specific summary."""
    summary = Summary.query.get_or_404(summary_id)
    db.session.delete(summary)
    db.session.commit()
    flash("Summary deleted.", "success")
    return redirect(url_for("admin.dashboard"))
