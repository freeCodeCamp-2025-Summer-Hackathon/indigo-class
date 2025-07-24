from flask import (
    Blueprint,
    flash,
    redirect,
    request,
    render_template,
    url_for,
    current_app,
)
from flask_login import current_user, login_required
from app.models import db, User
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from ..auth import generate_reset_token
from flask_mail import Message
from app import mail

user_bp = Blueprint("user", __name__, url_prefix="/admin/user")


def split_name(full_name: str):
    """Split full name into first and last names."""
    name_parts = full_name.strip().split()
    first_name = name_parts[0] if name_parts else ""
    last_name = name_parts[1]
    return first_name, last_name


# View user list
@user_bp.route("/", methods=["GET"])
@login_required
def user_list():
    if not current_user.is_admin():
        flash("Unauthorized access.", "danger")
        return redirect(url_for("root.index"))

    # pagination with query
    page = request.args.get("page", 1, type=int)
    per_page = 20
    paginated_users = (
        User.query.options(joinedload(User.roles))
        .order_by(User.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    all_users = paginated_users.items

    user_summary = [
        {
            "user_id": user.user_id,
            "name": user.name,
            "first_name": split_name(user.name)[0],
            "last_name": split_name(user.name)[1],
            "username": user.username,
            "email": user.email,
            "is_email_opt_in": user.is_email_opt_in,
            "role_name": [role.name for role in user.roles],
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
        for user in all_users
    ]
    return render_template(
        "admin/user.html", user_summary=user_summary, pagination=paginated_users
    )


# Edit user
@user_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_user(user_id: int):
    if not current_user.is_admin():
        flash("Unauthorized access.", "danger")
        return redirect(url_for("root.index"))

    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        first_name = request.form.get("first_name").strip()
        last_name = request.form.get("last_name").strip()
        current_form = {
            "first_name": first_name,
            "last_name": last_name,
            "name": f"{first_name} {last_name}",
            "username": request.form.get("username"),
            "email": request.form.get("email"),
            "is_email_opt_in": request.form.get("is_email_opt_in") == "on",
        }

        # validate required fields
        required_fields: list[str] = ["first_name", "last_name", "username", "email"]
        for field in required_fields:
            if not current_form[field]:
                flash(f"Missing required field: {field}", "error")
                return render_template(
                    "admin/user/edit.html", user=user, form_data=current_form
                )

        # check if username or email already exists
        user_with_username = User.query.filter(
            and_(
                User.username == current_form["username"], User.user_id != user.user_id
            )
        ).first()
        if user_with_username:
            flash("Username already exists", "error")
            return render_template(
                "admin/user/edit.html", user=user, form_data=current_form
            )

        user_with_email = User.query.filter(
            and_(User.email == current_form["email"], User.user_id != user.user_id)
        ).first()
        if user_with_email:
            flash("Email already exists", "error")
            return render_template(
                "admin/user/edit.html", user=user, form_data=current_form
            )

        # update in db
        user.name = current_form["name"]
        user.username = current_form["username"]
        user.email = current_form["email"]
        user.is_email_opt_in = current_form["is_email_opt_in"]
        db.session.commit()
        flash("User information updated successfully.", "success")

    return render_template(
        "admin/user/edit.html",
        user=user,
        form_data={
            "name": user.name,
            "username": user.username,
            "email": user.email,
            "is_email_opt_in": user.is_email_opt_in,
        },
    )


# Delete user
@user_bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id: int):
    if not current_user.is_admin():
        flash("Unauthorized access.", "danger")
        return redirect(url_for("root.index"))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.", "warning")
    return redirect(
        url_for("user.user_list", page=request.args.get("page", 1, type=int))
    )


# Change email toggle
@user_bp.route("/<int:user_id>/toggle-email-optin", methods=["POST"])
@login_required
def toggle_email_subscription(user_id: int):
    if not current_user.is_admin():
        flash("Unauthorized access.", "danger")
        return redirect(url_for("root.index"))
    user = User.query.get_or_404(user_id)
    user.is_email_opt_in = not user.is_email_opt_in
    db.session.commit()
    flash(
        f"Email subscription {'enabled' if user.is_email_opt_in else 'disabled'}.",
        "info",
    )
    return redirect(
        url_for("user.user_list", page=request.args.get("page", 1, type=int))
    )


# Reset_password from admin
@user_bp.route("/<int:user_id>/reset_password", methods=["POST"])
@login_required
def admin_reset_password(user_id: int):
    if not current_user.is_admin():
        flash("Unauthorized access.", "danger")
        return redirect(url_for("root.index"))
    user = User.query.get_or_404(user_id)
    token = generate_reset_token(user.email)
    reset_url = url_for("auth.reset_password_token", token=token, _external=True)
    msg = Message(
        subject="Password Reset Request",
        recipients=[user.email],
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
    )
    msg.body = f"""To reset your password, click the following link: {reset_url}
                \n\n
                If you did not request a password reset,
                please ignore this email.
                """
    mail.send(msg)
    flash("Password reset email has been sent!", "success")
    return redirect(
        url_for("user.user_list", page=request.args.get("page", 1, type=int))
    )
