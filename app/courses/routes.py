from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app import login_required

courses_bp = Blueprint("courses", __name__)

COURSES = {
    "climate-data-analysis": {
        "title": "Climate Data Analysis",
        "subject": "Climate Science",
        "duration": "6 weeks",
    },
    "python-for-operational-meteorology": {
        "title": "Python for Operational Meteorology",
        "subject": "Python",
        "duration": "4 weeks",
    },
    "hydrology-and-risk-mapping": {
        "title": "Hydrology and Risk Mapping",
        "subject": "Hydrology",
        "duration": "5 weeks",
    },
}


@courses_bp.route("/")
def index():
    courses = [
        {"title": "Climate Data Analysis", "subject": "Climate Science", "duration": "6 weeks"},
        {"title": "Python for Operational Meteorology", "subject": "Python", "duration": "4 weeks"},
        {"title": "Hydrology and Risk Mapping", "subject": "Hydrology", "duration": "5 weeks"},
    ]
    return render_template("courses.html", courses=courses)


@courses_bp.route("/<course_id>")
def detail(course_id):
    course = COURSES.get(course_id)
    if not course:
        return render_template("404.html"), 404
    return render_template("course_detail.html", course_id=course_id, course=course)


@courses_bp.route("/enroll/<course_id>", methods=["POST"])
@login_required("trainee")
def enroll(course_id):
    if course_id not in COURSES:
        return render_template("404.html"), 404

    session.setdefault("enrolled_courses", [])
    if course_id not in session["enrolled_courses"]:
        session["enrolled_courses"].append(course_id)
    session.modified = True
    flash("You have enrolled in the course.", "success")
    return redirect(url_for("trainee.courses"))
