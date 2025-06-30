import os
from datetime import datetime

from flask import Flask, jsonify


def create_app():
    """
    Main entry point for the web application.
    """
    app = Flask(__name__)

    app.config.from_mapping(SECRET_KEY=os.environ.get("SECRET_KEY", "dev"))

    app.static_folder = "static"
    app.template_folder = "templates"

    from .controllers.root import root_bp

    app.register_blueprint(root_bp)

    @app.route("/health")
    def health_check():
        return jsonify(
            {
                "status": "running",
                "timestamp": datetime.now().isoformat(),
                "version": "0.1.0",
            }
        )

    return app
