from flask import Blueprint, render_template, session

from app import login_required
from app.courses.routes import COURSES

trainee_bp = Blueprint("trainee", __name__)


def get_trainee_courses():
    enrolled = session.get("enrolled_courses", [])
    items = []
    for course_id in enrolled:
        course = COURSES.get(course_id)
        if course:
            items.append({
                "id": course_id,
                "title": course["title"],
                "subject": course["subject"],
                "progress": 68,
            })
    return items


@trainee_bp.route("/dashboard")
@login_required("trainee")
def dashboard():
    user = session.get("user", {})
    enrolled_courses = get_trainee_courses()
    trainee_profile = {
        "name": user.get("name") or "Trainee",
        "email": user.get("email") or "N/A",
        "department": "Climate Services",
        "progress": 68 if enrolled_courses else 0,
        "courses": enrolled_courses,
        "assessments": [],
        "certificates": [],
    }
    return render_template(
        "trainee_dashboard.html",
        user=trainee_profile,
        courses=trainee_profile["courses"],
        assessments=trainee_profile["assessments"],
        certificates=trainee_profile["certificates"],
    )


@trainee_bp.route("/profile")
@login_required("trainee")
def profile():
    user = session.get("user", {})
    profile_data = {
        "full_name": user.get("name") or "Trainee",
        "email": user.get("email") or "N/A",
        "qualification": "M.Sc. Meteorology",
        "phone": "+91 90000 00000",
    }
    return render_template("trainee_profile.html", user=profile_data)


@trainee_bp.route("/courses")
@login_required("trainee")
def courses():
    return render_template("trainee_courses.html", courses_data={course_id: course for course_id, course in COURSES.items() if course_id in session.get("enrolled_courses", [])})


@trainee_bp.route("/competencies")
@login_required("trainee")
def competencies():
    return render_template("trainee_competencies.html")
