from datetime import datetime
from typing import List

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db
from app.models import User, Affirmation

root_bp = Blueprint("root", __name__)


@root_bp.route("/")
def index():
    """
    Main landing page.
    """

    return render_template(
        "home/index.html",
        title="DailyDose",
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


@root_bp.route("/dashboard")
@login_required
def dashboard():
    """
    User dashboard - requires authentication.
    """
    return render_template(
        "home/dashboard.html",
        title="Dashboard",
        user=current_user,
    )


@root_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    """
    Admin dashboard - requires authentication.
    """
    all_users: List[User] = User.query.all()
    all_affirmations: List[Affirmation] = Affirmation.query.all()

    return render_template(
        "home/admin_dashboard.html",
        title="Admin Dashboard",
        user=current_user,
        all_users=all_users,
        all_affirmations=all_affirmations,
    )


@root_bp.route("/affirmations")
def affirmations():
    """
    Affirmations page.
    """
    all_affirmations: List[Affirmation] = Affirmation.query.all()
    return render_template("affirmations/index.html", all_affirmations=all_affirmations)


@root_bp.route("/affirmations/add", methods=["GET", "POST"])
@login_required
def add_affirmation():
    """
    Add an affirmation
    """
    if request.method == "POST":
        text: str | None = request.form.get("affirmation_text")

        if not text:
            flash("Please type your affirmation", "error")
            return render_template("affirmations/add.html")

        affirmation = Affirmation(affirmation_text=text, user_id=current_user.user_id)

        db.session.add(affirmation)
        db.session.commit()

        flash("Your affirmation have been added", "success")
        return redirect(url_for("root.affirmations"))

    return render_template("affirmations/add.html")


@root_bp.route("/affirmations/edit/<int:affirmation_id>", methods=["GET", "POST"])
@login_required
def edit_affirmation(affirmation_id):
    affirmation = Affirmation.query.get_or_404(affirmation_id)
    if affirmation.user_id != current_user.user_id:
        flash("Can not edit others affirmation", "error")
        return redirect(url_for("root.affirmations"))

    if request.method == "POST":
        textInput: str | None = request.form.get("affirmation_text")

        if not textInput:
            return render_template("affirmations/edit.html", affirmation=affirmation)

        affirmation.affirmation_text = textInput
        db.session.commit()

        flash("Affirmation updated", "success")
        return redirect(url_for("root.affirmations"))

    return render_template("affirmations/edit.html", affirmation=affirmation)
