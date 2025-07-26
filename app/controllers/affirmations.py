from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from threading import Timer

from app import db, globals
from app.models import (
    Affirmation,
    SavedAffirmation,
    Category,
    AffirmationCategory,
    UserAffirmation,
)

affirmations_bp = Blueprint("affirmations", __name__)


@affirmations_bp.route("/affirmations")
def affirmations():
    """
    Affirmations page.
    """
    MAX_PER_PAGE = 20
    page_num = request.args.get("page", 1, type=int)
    category = request.args.get("category")

    if category:
        paginated_affirmations = (
            Affirmation.query.join(AffirmationCategory)
            .join(Category)
            .filter(Category.name == category)
            .paginate(per_page=MAX_PER_PAGE, page=page_num, error_out=True)
        )
    else:
        paginated_affirmations = Affirmation.query.paginate(
            per_page=MAX_PER_PAGE, page=page_num, error_out=True
        )

    categories = Category.query.all()
    return render_template(
        "affirmations/index.html",
        all_affirmations=paginated_affirmations,
        user=current_user,
        categories=categories,
    )


@affirmations_bp.route("/affirmations/random", methods=["GET"])
def random_affirmation():
    """
    Get a random affirmation, optionally filtered by category.
    Rate limited to one request per 10 seconds.
    """
    # Check rate limit
    if not current_user.is_authenticated:
        client_ip = request.remote_addr
        key = f"random_affirmation:{client_ip}"
    else:
        key = f"random_affirmation:{current_user.user_id}"

    # Check if key exists in rate limit dict
    if key in globals.rate_limit_dict:
        return jsonify({"error": "Please wait 10 seconds for next request"}), 429

    # Set rate limit
    globals.rate_limit_dict[key] = True

    # Remove rate limit after 10 seconds
    def remove_rate_limit():
        if key in globals.rate_limit_dict:
            del globals.rate_limit_dict[key]

    Timer(10.0, remove_rate_limit).start()

    category = request.args.get("category")
    if category and category != "all":
        random_affirmation = (
            Affirmation.query.join(AffirmationCategory)
            .join(Category)
            .filter(Category.category_id == category)
            .order_by(func.random())
            .first()
        )
    else:
        random_affirmation = Affirmation.query.order_by(func.random()).first()

    if not random_affirmation:
        return jsonify({"error": "No affirmations found"}), 404

    # Serialize categories as a list of category names
    category_names = [ac.category.name for ac in random_affirmation.categories]
    return jsonify(
        {
            "affirmation": random_affirmation.affirmation_text,
            "categories": category_names,
        }
    )


@affirmations_bp.route("/affirmations/add", methods=["GET", "POST"])
@login_required
def add_affirmation():
    """
    Add an affirmation
    """
    if request.method == "POST":
        text: str | None = request.form.get("affirmation_text")

        if text is None or text.strip() == "":
            flash("Please type your affirmation", "error")
            return render_template("affirmations/add.html")

        affirmation = Affirmation(affirmation_text=text, user_id=current_user.user_id)

        db.session.add(affirmation)
        db.session.commit()

        flash("Your affirmation has been added", "success")
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


@affirmations_bp.post("/affirmations/select-category")
@login_required
def select_affirmation_category():
    # Get affirmation and category id
    data = request.get_json()
    affirmation_id = data.get("affirmationId")
    category_id = data.get("categoryId")

    if affirmation_id is None or category_id is None:
        return jsonify({"error": "No affirmation or category ID provided"}), 400

    # Check if affirmations_categories row have already existed
    affirmation_category = AffirmationCategory.query.filter_by(
        affirmation_id=affirmation_id, category_id=category_id
    ).first()
    # prevent double data
    if affirmation_category:
        return jsonify({"error": "Affirmation category already selected"}), 400

    # Check if affirmation exists
    affirmation = Affirmation.query.get(affirmation_id)
    if affirmation is None:
        return jsonify({"error": "Affirmation not found"}), 404

    # Check if category exists (allow admin or user category)
    category = Category.query.filter_by(category_id=category_id).first()
    if category is None or (
        not category.is_admin_set and category.user_id != current_user.user_id
    ):
        return jsonify({"error": "Category doesn't exist"}), 400

    # Add affirmations_categories row
    affirmation_category = AffirmationCategory(
        affirmation_id=affirmation_id, category_id=category_id
    )

    db.session.add(affirmation_category)
    db.session.commit()
    return jsonify({"message": "category selected"}), 200


ACTION_TYPES_LIMIT_DICT = {"pin": 3, "favorite": 15}


@affirmations_bp.post("/affirmations/action/<action_type>")
@login_required
def add_user_affirmation_with_action_type(action_type):
    # validate action_type
    if action_type not in ACTION_TYPES_LIMIT_DICT.keys():
        return jsonify({"error": f"Invalid action type: {action_type}"}), 400

    data = request.get_json()
    affirmation_id = data.get("affirmationId")

    # check if action type already reach limit
    affirmation_count = (
        db.session.query(UserAffirmation)
        .filter(
            UserAffirmation.user_id == current_user.user_id,
            UserAffirmation.action_type == action_type,
        )
        .count()
    )
    if affirmation_count >= ACTION_TYPES_LIMIT_DICT[action_type]:
        return jsonify({"error": f"{action_type} already limited"}), 400

    # check if affirmation exists
    affirmation = Affirmation.query.get(affirmation_id)
    if affirmation is None:
        return jsonify({"error": "Affirmation not found"}), 404

    # insert users_affirmations
    try:
        insert_statement = (
            insert(UserAffirmation)
            .values(
                affirmation_id=affirmation_id,
                user_id=current_user.user_id,
                action_type=action_type,
            )
            .on_conflict_do_nothing(constraint="user_affirmation_uc")
        )

        db.session.execute(insert_statement)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "an error occurred: {}".format(e)}), 500

    # refresh page
    request_referrer = request.referrer
    if not request_referrer:
        return redirect(url_for("root.index"))

    return redirect(request_referrer)
