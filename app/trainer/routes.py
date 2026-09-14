from flask import Blueprint, render_template, session

from app import login_required

trainer_bp = Blueprint("trainer", __name__)


@trainer_bp.route("/dashboard")
@login_required("trainer")
def dashboard():
    user = session.get("user", {})
    trainer_profile = {
        "name": user.get("name") or "Trainer",
        "email": user.get("email") or "N/A",
        "role": "Trainer",
        "department": "Training & Competency Development",
        "courses_created": 8,
        "active_trainees": 132,
        "average_score": "84%",
        "specialization": "Meteorological Data, Python, Climate Analytics",
    }
    return render_template("trainer_dashboard.html", user=trainer_profile, stats={
        "courses_created": trainer_profile["courses_created"],
        "active_trainees": trainer_profile["active_trainees"],
        "average_score": trainer_profile["average_score"],
    })


@trainer_bp.route("/courses")
@login_required("trainer")
def courses():
    return render_template("trainer_courses.html")


@trainer_bp.route("/library")
@login_required("trainer")
def library():
    return render_template("trainer_library.html")
