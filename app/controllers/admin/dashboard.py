from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from app.models import User, Affirmation, Category


dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/admin/dashboard")


@dashboard_bp.route("/", methods=["GET"])
@login_required
def dashboard():
    if not current_user.is_admin():
        flash("Unauthorized access.", "danger")
        return redirect(url_for("root.index"))
    stats_summary = {
        "total_users": User.query.count(),
        "total_affirmations": Affirmation.query.count(),
        "total_categories": Category.query.count(),
    }

    return render_template("admin/dashboard.html", stats_summary=stats_summary)
