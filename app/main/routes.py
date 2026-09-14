from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    featured_courses = [
        {"title": "Data Analytics Foundations", "subject": "Data", "duration": "4 weeks"},
        {"title": "Python for Meteorological Data", "subject": "Python", "duration": "6 weeks"},
        {"title": "Climate Risk Communication", "subject": "Climate", "duration": "3 weeks"},
    ]
    announcements = [
        {"title": "New meteorology training cohort", "text": "Applications open for the October learning cycle."},
        {"title": "Assessment window update", "text": "MCQ and questionnaire deadlines are now visible in dashboards."},
    ]
    achievements = [
        {"title": "1200+ learners certified", "text": "Across operational weather and climate programs."},
        {"title": "18 trainers onboarded", "text": "with domain expertise across hazard monitoring and data science."},
    ]
    content = [
        {"title": "Remote sensing module", "text": "New practical case study library added."},
        {"title": "Forecasting workshop toolkit", "text": "Field-ready templates and briefing notes released."},
    ]
    return render_template(
        "index.html",
        featured_courses=featured_courses,
        announcements=announcements,
        achievements=achievements,
        content=content,
    )


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/courses")
def public_courses():
    return render_template("public_courses.html")
