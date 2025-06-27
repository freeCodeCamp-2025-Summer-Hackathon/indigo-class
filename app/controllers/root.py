from datetime import datetime

from flask import Blueprint, render_template

root_bp = Blueprint("root", __name__)


@root_bp.route("/")
def index():
    """
    Main landing page.
    """

    return render_template(
        "home/index.html",
        title="Indigo-Class",
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
