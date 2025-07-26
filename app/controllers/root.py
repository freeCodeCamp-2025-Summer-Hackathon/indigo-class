from datetime import datetime
from typing import List

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from app.models import User, Affirmation, UserAffirmation, Category, DailyMailHistory

from app import db
from .. import globals

root_bp = Blueprint("root", __name__)


@root_bp.route("/")
def index():
    """
    Main landing page.
    """
    all_affirmations: List[Affirmation] = Affirmation.query.all()
    if current_user.is_authenticated:
        all_categories: List[Category] = Category.query.filter(
            Category.user_id == current_user.user_id
        ).all()
    else:
        all_categories: List[Category] = Category.query.filter(
            Category.is_admin_set.is_(True)
        ).all()

    pinned_affirmations = None
    if current_user.is_authenticated:
        pinned_affirmations = (
            db.session.query(Affirmation)
            .join(
                UserAffirmation,
                UserAffirmation.affirmation_id == Affirmation.affirmation_id,
            )
            .filter(
                UserAffirmation.user_id == current_user.user_id,
                UserAffirmation.action_type == "pin",
            )
            .all()
        )

    return render_template(
        "home/index.html",
        title="DailyDose",
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user=current_user,
        all_affirmations=all_affirmations,
        pinned_affirmations=pinned_affirmations,
        daily_affirmation_data=globals.daily_affirmation_data,
        all_categories=all_categories,
    )


@root_bp.route("/dashboard")
@login_required
def dashboard():
    """
    User dashboard - requires authentication.
    """
    # get user's pinned affirmations
    pinned_affirmations = (
        db.session.query(Affirmation)
        .join(
            UserAffirmation,
            UserAffirmation.affirmation_id == Affirmation.affirmation_id,
        )
        .filter(
            UserAffirmation.user_id == current_user.user_id,
            UserAffirmation.action_type == "pin",
        )
        .all()
    )

    # get user's favorite affirmations
    favorite_affirmations = (
        db.session.query(Affirmation)
        .join(
            UserAffirmation,
            UserAffirmation.affirmation_id == Affirmation.affirmation_id,
        )
        .filter(
            UserAffirmation.user_id == current_user.user_id,
            UserAffirmation.action_type == "favorite",
        )
        .all()
    )

    # get user's categories
    user_categories = (
        db.session.query(Category)
        .filter(Category.user_id == current_user.user_id)
        .all()
    )

    admin_categories = (
        db.session.query(Category).filter(Category.is_admin_set.is_(True)).all()
    )

    return render_template(
        "home/dashboard.html",
        title="Dashboard",
        user=current_user,
        pinned_affirmations=pinned_affirmations,
        favorite_affirmations=favorite_affirmations,
        user_categories=user_categories,
        admin_categories=admin_categories,
    )


@root_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    """
    Admin dashboard - requires authentication.
    """
    if not current_user.is_admin():
        return redirect(url_for("root.index"))
    return render_template(
        "admin/dashboard.html",
        title="Admin Dashboard",
        user=current_user,
        total_users=User.query.count(),
        total_affirmations=Affirmation.query.count(),
        total_categories=Category.query.count(),
        total_daily_emails=DailyMailHistory.query.count(),
    )


@root_bp.route("/admin/dashboard/users")
@login_required
def admin_dashboard_users():
    """
    Admin dashboard - requires authentication.
    """
    if not current_user.is_admin():
        return redirect(url_for("root.index"))

    all_users: List[User] = User.query.all()
    return render_template(
        "admin/dashboard_users.html",
        title="Users",
        user=current_user,
        all_users=all_users,
    )


@root_bp.route("/admin/dashboard/affirmations")
@login_required
def admin_dashboard_affirmations():
    """
    Admin dashboard - requires authentication.
    """
    if not current_user.is_admin():
        return redirect(url_for("root.index"))

    all_affirmations: List[Affirmation] = Affirmation.query.all()
    return render_template(
        "admin/dashboard_affirmations.html",
        title="Affirmations",
        user=current_user,
        all_affirmations=all_affirmations,
    )


@root_bp.route("/admin/dashboard/categories")
@login_required
def admin_dashboard_categories():
    """
    Admin dashboard - requires authentication.
    """
    if not current_user.is_admin():
        return redirect(url_for("root.index"))

    all_categories: List[Category] = Category.query.all()
    return render_template(
        "admin/dashboard_categories.html",
        title="Categories",
        user=current_user,
        all_categories=all_categories,
    )


@root_bp.route("/admin/dashboard/daily-mail-history")
@login_required
def admin_dashboard_daily_mail_history():
    """
    Admin dashboard - requires authentication.
    """
    if not current_user.is_admin():
        return redirect(url_for("root.index"))

    daily_mail_history: List[DailyMailHistory] = DailyMailHistory.query.all()
    return render_template(
        "admin/dashboard_daily_mail_history.html",
        title="Daily Mail History",
        user=current_user,
        daily_mail_history=daily_mail_history,
    )
