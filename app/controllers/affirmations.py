from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from typing import List
from sqlalchemy import func

from app import db
from app.models import Affirmation, SavedAffirmation

affirmations_bp = Blueprint("affirmations", __name__)


@affirmations_bp.route("/affirmations")
def affirmations():
    """
    Affirmations page.
    """
    all_affirmations: List[Affirmation] = Affirmation.query.all()
    return render_template(
        "affirmations/index.html", all_affirmations=all_affirmations, user=current_user
    )


@affirmations_bp.route("/affirmations/random", methods=["GET"])
def random_affirmation():
    """
    Affirmations page.
    """
    random_affirmation: Affirmation = Affirmation.query.order_by(func.random()).first()
    return jsonify({"affirmation": random_affirmation.affirmation_text})


@affirmations_bp.route("/affirmations/add", methods=["GET", "POST"])
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
        return redirect(url_for("affirmations.affirmations"))

    return render_template("affirmations/add.html")


@affirmations_bp.route(
    "/affirmations/edit/<int:affirmation_id>", methods=["GET", "POST"]
)
@login_required
def edit_affirmation(affirmation_id):
    affirmation = Affirmation.query.get_or_404(affirmation_id)
    if affirmation.user_id != current_user.user_id:
        flash("Can not edit others affirmation", "error")
        return redirect(url_for("affirmations.affirmations"))

    if request.method == "POST":
        textInput: str | None = request.form.get("affirmation_text")

        if not textInput:
            return render_template("affirmations/edit.html", affirmation=affirmation)

        affirmation.affirmation_text = textInput
        db.session.commit()

        flash("Affirmation updated", "success")
        return redirect(url_for("affirmations.affirmations"))

    return render_template("affirmations/edit.html", affirmation=affirmation)


@affirmations_bp.post("/affirmations/delete/<int:affirmation_id>")
@login_required
def delete_affirmation(affirmation_id):
    affirmation = Affirmation.query.get_or_404(affirmation_id)
    if affirmation.user_id == current_user.user_id:
        db.session.delete(affirmation)
        db.session.commit()
        flash("Affirmation deleted", "success")

    return redirect(url_for("affirmations.affirmations"))


@affirmations_bp.route("/affirmations/save", methods=["POST"])
@login_required
def save_affirmation():
    data = request.get_json()
    affirmation_id = data.get("affirmationId")
    if not affirmation_id:
        return jsonify({"error": "No affirmation ID provided"}), 400

    affirmation = Affirmation.query.get(affirmation_id)
    if not affirmation:
        return jsonify({"error": "Affirmation not found"}), 404

    # Check if already saved
    already_saved = SavedAffirmation.query.filter_by(
        user_id=current_user.user_id, affirmation_id=affirmation_id
    ).first()
    if already_saved:
        return jsonify({"message": "Already saved"}), 200

    saved = SavedAffirmation(
        user_id=current_user.user_id, affirmation_id=affirmation_id
    )
    db.session.add(saved)
    db.session.commit()
    return jsonify({"message": "Affirmation saved"}), 200


@affirmations_bp.route("/affirmations/unsave", methods=["POST"])
@login_required
def unsave_affirmation():
    data = request.get_json()
    affirmation_id = data.get("affirmationId")
    if not affirmation_id:
        return jsonify({"error": "No affirmation ID provided"}), 400

    saved = SavedAffirmation.query.filter_by(
        user_id=current_user.user_id, affirmation_id=affirmation_id
    ).first()
    if not saved:
        return jsonify({"error": "Affirmation not found"}), 404

    db.session.delete(saved)
    db.session.commit()
    return jsonify({"message": "Affirmation unsaved"}), 200
