from flask import Blueprint, render_template

feedback_bp = Blueprint("feedback", __name__)


@feedback_bp.route("/")
def index():
    return render_template("feedback.html")
