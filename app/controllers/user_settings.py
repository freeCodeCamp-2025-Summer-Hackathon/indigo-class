from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import current_user, login_required, logout_user
from app.models import db

usersettings_bp = Blueprint("user_settings", __name__, url_prefix="/user-settings")


# View user info
@usersettings_bp.route("/", methods=["GET"])
@login_required
def user_info():
    user = current_user
    name_parts = []
    name_parts = user.name.strip().split()
    firstname = name_parts[0]
    lastname = " ".join(name_parts[1:])
    user_summary = {
        "email": user.email,
        "is_email_opt_in": user.is_email_opt_in,
        "name": user.name,
        "username": user.username,
        "firstname": firstname,
        "lastname": lastname,
    }
    return render_template(
        "user_settings.html", user_summary=user_summary
    )  # profile.html?


# Edit user firstname, lastname, username, email
@usersettings_bp.route("/profile", methods=["POST"])
@login_required
def update_profile():
    user = current_user
    return redirect(url_for("usersettings.user_info"))


# Change password
@usersettings_bp.route("/password", methods=["POST"])
@login_required
def change_password():
    user = current_user
    return redirect(url_for("usersettings.user_info"))


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
