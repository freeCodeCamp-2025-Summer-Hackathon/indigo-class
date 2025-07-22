from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required, logout_user
from app.models import db, User
from sqlalchemy import and_
import bcrypt

usersettings_bp = Blueprint("user_settings", __name__, url_prefix="/user-settings")


# View user info
@usersettings_bp.route("/", methods=["GET"])
@login_required
def user_info():
    user = current_user
    name_parts = user.name.strip().split()
    first_name = name_parts[0]
    last_name = " ".join(name_parts[1:])
    user_summary = {
        "email": user.email,
        "is_email_opt_in": user.is_email_opt_in,
        "name": user.name,
        "username": user.username,
        "firstname": first_name,
        "lastname": last_name,
    }
    return render_template(
        "auth/user_settings.html", user_summary=user_summary
    )  # profile.html?


# Edit user first_name, last_name, username, email
@usersettings_bp.route("/profile", methods=["POST"])
@login_required
def update_profile():
    user = current_user

    if "first_name" in request.form or "last_name" in request.form:
        first = request.form.get("first_name", "").strip()
        last = request.form.get("last_name", "").strip()
        if not first or not last:
            flash("Both first and last names are required", "error")
            return redirect(url_for("usersettings.user_info"))
        name = f"{first} {last}".strip()
        user.name = name

    if "username" in request.form:
        username = request.form.get("username", "").strip()
        if not username:
            flash("Username is required.", "error")
            return redirect(url_for("usersettings.user_info"))

        user_username = User.query.filter(
            and_(User.username == username, User.user_id != user.user_id)
        ).first()
        if user_username:
            flash(f"Username: {username} already exists", "error")
            return redirect(url_for("usersettings.user_info"))
        user.username = username

    if "email" in request.form:
        email = request.form.get("email", "").strip()
        if not email:
            flash("Email is required.", "error")
            return redirect(url_for("usersettings.user_info"))

        user_email = User.query.filter(
            and_(User.email == email, User.user_id != user.user_id)
        ).first()
        if user_email:
            flash(f"Email: {email} already exists", "error")
            return redirect(url_for("usersettings.user_info"))
        user.email = email

    db.session.commit()
    flash("Update successfully.", "success")
    return redirect(url_for("usersettings.user_info"))


# Change password
@usersettings_bp.route("/password", methods=["POST"])
@login_required
def change_password():
    user = current_user
    password = request.form.get("password")

    if not password:
        flash("Password is required.", "error")
        return redirect(url_for("usersettings.user_info"))

    password_hash: str = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    user.password_hash = password_hash
    db.session.commit()
    flash(
        "Password updated successfully. Please log in with the new password.",
        "success",
    )
    logout_user()
    return redirect(url_for("auth.login"))


# Change email toggle
@usersettings_bp.route("/toggle-email-optin", methods=["POST"])
@login_required
def toggle_email_subscription():
    user = current_user
    user.is_email_opt_in = not user.is_email_opt_in
    db.session.commit()
    flash(
        f"Email subscription {'enabled' if user.is_email_opt_in else 'disabled'}.",
        "info",
    )
    return redirect(url_for("usersettings.user_info"))


# Delete user
@usersettings_bp.route("/delete", methods=["POST"])
@login_required
def delete_user():
    user = current_user
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.", "warning")
    return redirect(url_for("root.index"))
