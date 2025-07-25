from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_, select

from app import db
from app.models import Category

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/categories")
def list_categories():
    # per_page = request.args.get("per_page", 10, type=int)

    if current_user.is_authenticated:
        """Queries to be use for filtering and pagination
        authenticated users can only see global or admin set categories and categories that they made
        """
        all_categories = select(Category).where(
            or_(
                Category.is_admin_set.is_(True)
                | (Category.user_id == current_user.user_id)
            )
        )

        user_categories = select(Category).where(
            (
                Category.is_admin_set.is_(False)
                & (Category.user_id == current_user.user_id)
            )
        )

        admin_categories = select(Category).where(Category.is_admin_set.is_(True))

        filter_by = request.args.get("filter", "all_categories")
        page = request.args.get("page", 1, type=int)

        if filter_by == "user_categories":
            pagination = db.paginate(user_categories, page=page, per_page=5)
        elif filter_by == "admin_categories":
            pagination = db.paginate(admin_categories, page=page, per_page=5)
        else:
            pagination = db.paginate(all_categories, page=page, per_page=5)

    return render_template(
        "categories/list.html",
        categories=pagination.items,
        pagination=pagination,
        filter_by=filter_by,
    )


@categories_bp.route("/categories/add", methods=["GET", "POST"])
@login_required
def add_category():

    if request.method == "POST":
        category_name = request.form.get("name")

        if not category_name:
            flash("Name for the category is required", "error")
            return render_template("categories/add.html")

        user_has_category = Category.query.filter_by(
            user_id=current_user.user_id, name=category_name
        ).first()

        admin_has_category = Category.query.filter_by(
            is_admin_set=True, name=category_name
        ).first()

        # users can't add categories that already exists globally(admin created)
        # or if the user already created a category of the same name
        if user_has_category:
            flash("You have a category with the same name.", "error")
            return redirect(url_for("categories.add_category"))

        if admin_has_category:
            flash("That category name is reserved by admin.", "error")
            return redirect(url_for("categories.add_category"))

        new_category = Category(
            name=category_name, user_id=current_user.user_id, is_admin_set=False
        )

        db.session.add(new_category)
        db.session.commit()

        flash("Your category has been added successfully.", "success")
        return redirect(url_for("categories.list_categories"))

    return render_template("categories/add.html")


@categories_bp.route("/categories/edit/<int:category_id>", methods=["GET", "POST"])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    # pass page to return the user to the page where he/she did the action
    page = request.args.get("page") or request.form.get("page", 1)

    if category.user_id != current_user.user_id or category.is_admin_set:
        flash("You can only edit your own categories.", "danger")
        return redirect(url_for("categories.list_categories", page=page))

    if request.method == "POST":
        category_name = request.form["name"]

        is_existing_category = Category.query.filter(
            Category.name == category_name,
            Category.category_id != category.category_id,
            or_(
                Category.is_admin_set.is_(True)
                | (Category.user_id == current_user.user_id)
            ),
        ).first()

        if is_existing_category:
            flash("Category name already exists", "warning")
            return render_template("categories/edit.html", category=category)

        category.name = category_name
        db.session.commit()
        flash("You have successfully updated your category", "success")
        return redirect(url_for("categories.list_categories", page=page))

    return render_template("categories/edit.html", category=category, page=page)


@categories_bp.route("/categories/delete/<int:category_id>", methods=["GET", "POST"])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    # pass page to return the user to the page where he/she did the action
    page = request.args.get("page") or request.form.get("page", 1)

    # prevent deletion if its a global(admin set) category
    if category.is_admin_set:
        flash("You cannot delete categories made by admins.")
        return redirect(url_for("categories.list_categories", page=page))

    # prevents deletion if the current user doesn't own the category
    if category.user_id != current_user.user_id:
        flash("You can only delete your own categories.", "error")
        return redirect(url_for("categories.list_categories", page=page))

    db.session.delete(category)
    db.session.commit()
    flash("Category is successfully deleted", "success")
    return redirect(url_for("categories.list_categories", page=page))
