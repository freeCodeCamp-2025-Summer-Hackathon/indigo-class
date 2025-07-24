from datetime import datetime
from typing import List

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from app.models import User, Affirmation, UserAffirmation, Category

from app import db

root_bp = Blueprint("root", __name__)


@root_bp.route("/")
def index():
    """
    Main landing page.
    """
    all_affirmations: List[Affirmation] = Affirmation.query.all()

    admin_categories = (
        db.session.query(Category).filter(Category.is_admin_set.is_(True)).all()
    )

    return render_template(
        "home/index.html",
        title="DailyDose",
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user=current_user,
        all_affirmations=all_affirmations,
        admin_categories=admin_categories,
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

    all_users: List[User] = User.query.all()
    all_affirmations: List[Affirmation] = Affirmation.query.all()

    return render_template(
        "admin/dashboard.html",
        title="Admin Dashboard",
        user=current_user,
        all_users=all_users,
        all_affirmations=all_affirmations,
    )
