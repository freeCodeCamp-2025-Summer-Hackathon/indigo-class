from datetime import datetime
import os

from flask import Flask, jsonify
from flask_login import LoginManager
from flask_mail import Mail

from app.models import User, db

import dotenv

dotenv.load_dotenv()

mail = Mail()


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
    from .controllers.user import user_bp
    from .controllers.affirmations import affirmations_bp

    app.register_blueprint(root_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(affirmations_bp)

    @app.route("/health")
    def health_check():
        try:
            db.engine.execute("SELECT 1")
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
