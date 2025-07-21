from datetime import datetime
from typing import List

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from app.models import User, Affirmation, Category, AffirmationCategory, UserAffirmation

from app import db

root_bp = Blueprint("root", __name__)


@root_bp.route("/")
def index():
    """
    Main landing page.
    """
    all_affirmations: List[Affirmation] = Affirmation.query.all()

    return render_template(
        "home/index.html",
        title="DailyDose",
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user=current_user,
        all_affirmations=all_affirmations,
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

    # create user's affirmation dictionary
    user_affirmations_by_categories = (
        db.session.query(
            Category.name.label("category_name"),
            Affirmation.affirmation_text.label("affirmation_text"),
        )
        .select_from(AffirmationCategory)
        .join(
            Affirmation,
            Affirmation.affirmation_id == AffirmationCategory.affirmation_id,
        )
        .join(Category, AffirmationCategory.category_id == Category.category_id)
        .filter(Affirmation.user_id == current_user.user_id)
        .all()
    )

    user_affirmations_dict = {}
    for affirmation in user_affirmations_by_categories:
        category_name = affirmation.category_name
        if category_name not in user_affirmations_dict:
            user_affirmations_dict[category_name] = []
        user_affirmations_dict[category_name].append(affirmation.affirmation_text)

    return render_template(
        "home/dashboard.html",
        title="Dashboard",
        user=current_user,
        user_affirmations_dict=user_affirmations_dict,
        pinned_affirmations=pinned_affirmations,
        favorite_affirmations=favorite_affirmations,
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
