from flask import (
    Blueprint,
    current_app,
    url_for,
    render_template,
    request,
    flash,
    redirect,
)
from app.models import User
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from flask_mail import Message

# from app import mail, need to add the SMTP config

reset_password_bp = Blueprint("reset_password", __name__, url_prefix="/reset_password")


# Check if the input account info is registered
def verify_account(username: str, email: str) -> Optional[User]:
    user = User.query.filter_by(username=username.strip()).first()
    if user and user.email.lower().strip() == email.lower().strip():
        return user
    return None


# Generate password reset token
def generate_reset_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "purpose": "reset_password",
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    # need to add SECRET_KEY


# Verify token and new password
@reset_password_bp.route("/<token>", methods=["GET", "POST"])
def reset_password_token(token):
    # POST part
    return render_template(
        "new_password.html", token=token
    )  # a new page to setup new pwd?


# Send password reset email
def send_password_reset_email(user, token):
    reset_url = url_for(
        "reset_password.reset_password_token", token=token, _external=True
    )
    msg = Message(
        subject="[DailyDose] Reset your password",
        sender=current_app.config["MAIL_USERNAME"],  # noreply@xxx.com
        recipients=[user.email],
        body=f""" Dear {user.username}:
        Here is the password reset link: {reset_url}
        Please reset your password through the link within 24 hours.""",
    )
    mail.send(msg)


# Request password reset email
@reset_password_bp.route("/", methods=["GET", "POST"])
def request_reset_token():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        user = verify_account(username, email)
        if not user:
            flash("Invalid username or email.", "warning")
            return render_template(
                "reset_password.html", form_data={"username": username, "email": email}
            )
        else:
            token = generate_reset_token(user.user_id)
            send_password_reset_email(user, token)
            flash("Password reset email has been sent!", "success")
            return redirect(url_for("root.index"))
    return render_template("reset_password.html")
