from typing import Union
import bcrypt
from flask import (
    Blueprint,
    Response,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
)
from flask_login import current_user, login_required, login_user, logout_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Message

from app import db, mail
from app.models import Role, User

auth_bp = Blueprint("auth", __name__)


def generate_reset_token(user_email: str) -> str:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(user_email, salt="password-reset-salt")


def verify_reset_token(token: str, expiration=3600) -> Union[str, None]:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=expiration)
    except (SignatureExpired, BadSignature):
        return None
    return email


email_body = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .container {{
            background-color: #f9f9f9;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .button {{
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 12px 25px;
            text-decoration: none;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .footer {{
            font-size: 0.9em;
            color: #666;
            margin-top: 30px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Password Reset Request</h2>
        </div>
        
        <p>Hello,</p>
        
        <p>We received a request to reset your password. To proceed with the password reset, please click the button below:</p>
        
        <div style="text-align: center;">
            <a href="{reset_url}" class="button">Reset Password</a>
        </div>
        
        <p>If you did not request a password reset, please ignore this email and ensure your account is secure.</p>
        
        <div class="footer">
            <p>This link will expire in 1 hour for security purposes.</p>
            <p>If you're having trouble clicking the button, copy and paste this URL into your browser:</p>
            <p style="word-break: break-all;">{reset_url}</p>
        </div>
    </div>
</body>
</html>
"""


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    if current_user.is_authenticated:
        return redirect(url_for("root.index"))

    if request.method == "POST":
        username: str = request.form.get("username")
        password: str = request.form.get("password")
        remember: bool = request.form.get("remember") == "on"

        if not username or not password:
            flash("Please provide both username and password", "error")
            return render_template("auth/login.html")

        user: User = User.query.filter_by(username=username).first()

        # check if user exists and password is correct
        if user and bcrypt.checkpw(
            password.encode("utf-8"), user.password_hash.encode("utf-8")
        ):
            login_user(user, remember=remember)
            next_page: str = request.args.get("next")

            # Check if user has admin role
            admin_role = Role.query.filter_by(name="admin").first()
            if admin_role and admin_role in user.roles:
                next_page = url_for("root.admin_dashboard")

            if not next_page or not next_page.startswith("/"):
                next_page = url_for("root.index")

            return redirect(next_page)
        else:
            flash("Invalid username or password", "error")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
    if current_user.is_authenticated:
        return redirect(url_for("root.index"))

    if request.method == "POST":
        # read form data
        name: str = request.form.get("first_name") + " " + request.form.get("last_name")
        username: str = request.form.get("username")
        email: str = request.form.get("email")
        password: str = request.form.get("password")
        is_email_opt_in: bool = request.form.get("is_email_opt_in") == "on"

        # validate required fields
        required_fields: list[str] = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
        ]
        for field in required_fields:
            if not request.form.get(field):
                flash(f"Missing required field: {field}", "error")
                return render_template("auth/register.html")

        # check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists", "error")
            return render_template("auth/register.html")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists", "error")
            return render_template("auth/register.html")

        # hash password
        password_hash: str = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # create user
        user = User(
            name=name,
            username=username,
            email=email,
            password_hash=password_hash,
            is_email_opt_in=is_email_opt_in,
        )

        role = Role.query.filter_by(name="user").first()
        user.roles.append(role)

        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout() -> Response:
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile")
@login_required
def profile() -> str:
    return render_template("auth/profile.html", user=current_user)


@auth_bp.route("/reset_password", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("root.index"))
    if request.method == "POST":
        email = request.form.get("email")
        if not email:
            flash("Please enter your email address.", "error")
            return render_template("auth/reset_password_request.html")
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(user.email)
            reset_url = url_for("auth.new_password", token=token, _external=True)
            msg = Message(
                subject="Password Reset Request",
                recipients=[user.email],
                sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
            )
            msg.html = email_body.format(reset_url=reset_url)
            mail.send(msg)
        # Always flash the same message to prevent user enumeration
        flash(
            "If an account with that email exists, a password reset link has been sent.",
            "info",
        )
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password_request.html")


@auth_bp.route("/new_password/<token>", methods=["GET", "POST"])
def new_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("root.index"))
    email = verify_reset_token(token)

    if not email:
        flash("The password reset link is invalid or has expired.", "error")
        return redirect(url_for("auth.reset_password_request"))

    if request.method == "POST":
        password = request.form.get("new__password")
        password2 = request.form.get("confirm__password")

        if not password or not password2:
            flash("Please fill out both password fields.", "error")
            return render_template("auth/new_password.html", token=token)

        if password != password2:
            flash("Passwords do not match.", "error")
            return render_template("auth/new_password.html", token=token)
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User not found.", "error")
            return redirect(url_for("auth.reset_password_request"))

        user.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        db.session.commit()

        flash("Your password has been reset. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/new_password.html", token=token)


# use this to send a reset password email
# fetch("/reset_password", {
#     method: "POST",
#     headers: {
#         "Content-Type": "application/json",
#     },
#     body: JSON.stringify({ email: "test@example.com" }),
# });
