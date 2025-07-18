from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from app import db
from app.models import Category

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/categories")
def list_categories():
    if current_user.is_authenticated:
        categories = Category.query.filter(
            or_(
                Category.is_admin_set.is_(True)
                | (Category.user_id == current_user.user_id)
            )
        ).all()
    else:
        categories = Category.query.filter_by(is_admin_set=True).all()

    return render_template("category/list.html", categories=categories)


@categories_bp.route("/categories/add", methods=["GET", "POST"])
@login_required
def add_category():

    if request.method == "POST":
        category_name = request.form.get("name")

        if not category_name:
            flash("Name for the category is required", "error")
            return render_template("category.add_category.html")

        new_category = Category(
            name=category_name, user_id=current_user.user_id, is_admin_set=False
        )

        db.session.add(new_category)
        db.session.commit()

        flash("Your category has been added successfully.", "success")
        return redirect(url_for("categories.list_categories"))

    return render_template("category/add.html")


@categories_bp.route("/categories/edit/<int:category_id>", methods=["GET", "POST"])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)

    if category.user_id != current_user.id:
        flash("You can only edit your own categories.", "error")
        return redirect(url_for("category.list_categories"))

    if request.method == "POST":
        category.name = request.form["name"]
        db.session.commit()
        flash("You have successfully updated your category")
        return redirect(url_for("categories.list_categories"))

    return render_template("category/edit.html", category=category)


@categories_bp.route("/categories/delete/<int:category_id>", methods=["GET", "POST"])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)

    if category.user_id != current_user.id:
        flash("You can only delete your own categories.", "error")
        return redirect(url_for("category.list_categories"))

    db.session.delete(category)
    db.session.commit()
    flash("Category is successfully deleted", "success")
    return redirect(url_for("category.list_categories"))
