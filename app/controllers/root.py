from datetime import datetime
from typing import List

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from app.models import User, Affirmation, UserAffirmation, Category, DailyMailHistory
from app import db
from app.globals import daily_affirmation_data, daily_affirmation_date


root_bp = Blueprint("root", __name__)


@root_bp.route("/")
def index():
    """
    Main landing page.
    """
    global daily_affirmation_data, daily_affirmation_date

    # Check if we need to reset the daily affirmation (new day)
    today = datetime.now().date()
    if daily_affirmation_date != today:
        daily_affirmation_data = None
        daily_affirmation_date = today

    all_affirmations: List[Affirmation] = Affirmation.query.all()
    if current_user.is_authenticated:
        # Get both user's own categories and admin categories, excluding duplicates
        # by using distinct() to prevent duplicate categories when admin and user
        # have categories with the same name
        from sqlalchemy import distinct

        # First get all category names that the user should see
        category_names = (
            db.session.query(distinct(Category.name))
            .filter(
                (Category.user_id == current_user.user_id)
                | (Category.is_admin_set.is_(True))
            )
            .order_by(Category.name)
            .all()
        )

        # Then get the actual category objects, preferring admin categories over user categories
        all_categories = []
        for (name,) in category_names:
            # Try to get admin category first, then user category
            category = (
                Category.query.filter(
                    Category.name == name, Category.is_admin_set.is_(True)
                ).first()
                or Category.query.filter(
                    Category.name == name, Category.user_id == current_user.user_id
                ).first()
            )
            if category:
                all_categories.append(category)
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

    # Use the global daily affirmation data instead of generating a new random one
    # If no daily affirmation is set yet, set it once and use it consistently
    if daily_affirmation_data is None:
        try:
            daily_affirmation = Affirmation.query.order_by(db.func.random()).first()
            if daily_affirmation:
                try:
                    category_name = (
                        daily_affirmation.categories[0].category.name
                        if daily_affirmation.categories
                        else "General"
                    )
                except (IndexError, AttributeError):
                    category_name = "General"

                # Set the global variable once
                daily_affirmation_data = {
                    "id": daily_affirmation.affirmation_id,
                    "content": daily_affirmation.affirmation_text,
                    "category": category_name,
                }
                print(
                    f"Daily affirmation set for today ({today}): {daily_affirmation_data['content'][:50]}..."
                )
        except Exception as e:
            # Tables might not exist yet (e.g., during seeding)
            print(f"Error getting daily affirmation: {e}")
            pass

    # Check if daily affirmation is pinned by current user
    daily_affirmation_pinned = False
    if current_user.is_authenticated and daily_affirmation_data:
        daily_affirmation_pinned = (
            db.session.query(UserAffirmation)
            .filter(
                UserAffirmation.user_id == current_user.user_id,
                UserAffirmation.affirmation_id == daily_affirmation_data["id"],
                UserAffirmation.action_type == "pin",
            )
            .first()
            is not None
        )

    return render_template(
        "home/index.html",
        title="DailyDose",
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user=current_user,
        all_affirmations=all_affirmations,
        pinned_affirmations=pinned_affirmations,
        daily_affirmation_data=daily_affirmation_data,
        daily_affirmation_pinned=daily_affirmation_pinned,
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

    # get user's categories based on permissions
    if current_user.is_admin():
        # Admin can see all categories
        categories = Category.query.all()
        user_categories = Category.query.filter(
            Category.user_id == current_user.user_id
        ).all()
        admin_categories = Category.query.filter(Category.is_admin_set.is_(True)).all()
    else:
        # Regular users can only see their own categories
        categories = Category.query.filter(
            Category.user_id == current_user.user_id
        ).all()
        user_categories = Category.query.filter(
            Category.user_id == current_user.user_id
        ).all()
        admin_categories = []

    return render_template(
        "home/dashboard.html",
        title="Dashboard",
        user=current_user,
        pinned_affirmations=pinned_affirmations,
        favorite_affirmations=favorite_affirmations,
        categories=categories,
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
