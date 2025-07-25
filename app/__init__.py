from datetime import datetime
import os

from apscheduler.schedulers.background import BackgroundScheduler
import dotenv
from flask import Flask, current_app, jsonify
from flask_login import LoginManager
from flask_mail import Mail, Message
from sqlalchemy import text

from app.models import Affirmation, DailyMailHistory, User, db

dotenv.load_dotenv()

mail = Mail()
scheduler = BackgroundScheduler()

daily_affirmations = ""


def send_daily_emails():
    with current_app.app_context():
        users = User.query.filter_by(is_email_opt_in=True).all()
        today = datetime.now().date()

        for user in users:
            # Check if email already sent today
            already_sent = DailyMailHistory.query.filter(
                DailyMailHistory.user_id == user.user_id,
                db.func.date(DailyMailHistory.sent_email_at) == today,
                DailyMailHistory.success,
            ).first()

            if already_sent:
                continue

            affirmation = Affirmation.query.order_by(db.func.random()).first()
            if not affirmation:
                continue

            # Send email
            msg = Message(
                subject="Your Daily Affirmation",
                recipients=[user.email],
                body=f"Hello {user.name},\n\nYour affirmation for today:\n\n{affirmation.affirmation_text}\n\nHave a great day!",
            )
            history = DailyMailHistory(
                user_id=user.user_id,
                affirmation_id=affirmation.affirmation_id,
                sent_email_at=datetime.now(),
                success=False,  # Assume failure by default
                error_message=None,
            )
            db.session.add(history)
            db.session.flush()  # Ensures history gets an ID if needed

            try:
                mail.connect()
                mail.send(msg)
                history.success = True
            except Exception as e:
                history.error_message = str(e)
                print(f"Failed to send email to {user.email}: {e}")
            finally:
                db.session.commit()


def create_app():
    """
    Main entry point for the web application.
    """
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAIL_SERVER=os.environ.get("MAIL_SERVER"),
        MAIL_PORT=int(os.environ.get("MAIL_PORT", 587)),
        MAIL_USERNAME=os.environ.get("MAIL_USERNAME"),
        MAIL_DEFAULT_SENDER=os.environ.get("MAIL_DEFAULT_SENDER"),
        MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD"),
        MAIL_USE_TLS=os.environ.get("MAIL_USE_TLS", "False").lower() == "true",
        MAIL_USE_SSL=os.environ.get("MAIL_USE_SSL", "False").lower() == "true",
    )

    mail.init_app(app)

    app.static_folder = "static"
    app.template_folder = "templates"

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login."""
        return User.query.get(int(user_id))

    from .controllers.root import root_bp
    from .controllers.auth import auth_bp
    from .controllers.admin.user import user_bp
    from .controllers.affirmations import affirmations_bp
    from .controllers.categories import categories_bp
    from .controllers.user_settings import usersettings_bp

    app.register_blueprint(root_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(affirmations_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(usersettings_bp)

    # Start scheduler only if not already running
    if not scheduler.running:
        scheduler.add_job(send_daily_emails, "cron", hour=7, minute=0)  # 7:00 AM daily
        scheduler.start()

    @app.route("/test-email")
    def test_email():
        send_daily_emails()
        return jsonify({"message": "Email sent"}), 200

    @app.route("/health")
    def health_check():
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"

        return (
            jsonify(
                {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "version": "0.1.0",
                    "database": {
                        "status": db_status,
                    },
                }
            ),
            200,
        )

    return app
