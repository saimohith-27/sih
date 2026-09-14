from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app import login_required

assessments_bp = Blueprint("assessments", __name__)

ASSESSMENTS = {
    "weather-quiz": {
        "title": "Weather Data Quiz",
        "questions": {
            "q1": {"answer": "b", "points": 1},
            "q2": {"answer": "d", "points": 1},
        },
        "pass_mark": 60,
    },
    "python-competency": {
        "title": "Python Competency Check",
        "questions": {
            "q1": {"answer": "a", "points": 1},
            "q2": {"answer": "c", "points": 1},
        },
        "pass_mark": 60,
    },
}


def score_assessment(assessment_id, selected_answers):
    assessment = ASSESSMENTS.get(assessment_id)
    if not assessment:
        raise ValueError("Assessment not found")

    total_questions = len(assessment["questions"])
    if total_questions == 0:
        return {"score": 0, "percentage": 0, "passed": False}

    correct_count = 0
    for question_key, question in assessment["questions"].items():
        if selected_answers.get(question_key) == question["answer"]:
            correct_count += 1

    score = correct_count
    percentage = round((score / total_questions) * 100)
    passed = percentage >= assessment["pass_mark"]
    return {"score": score, "percentage": percentage, "passed": passed}


@assessments_bp.route("/")
@login_required(["trainee", "trainer", "admin"])
def index():
    return render_template("assessments.html")


@assessments_bp.route("/<assessment_id>")
@login_required(["trainee", "trainer", "admin"])
def detail(assessment_id):
    assessment = ASSESSMENTS.get(assessment_id)
    if not assessment:
        return render_template("404.html"), 404
    return render_template("assessment_detail.html", assessment_id=assessment_id, assessment=assessment)


@assessments_bp.route("/<assessment_id>/submit", methods=["POST"])
@login_required("trainee")
def submit(assessment_id):
    assessment = ASSESSMENTS.get(assessment_id)
    if not assessment:
        return render_template("404.html"), 404

    selected_answers = {key: value for key, value in request.form.items() if key.startswith("q")}
    result = score_assessment(assessment_id, selected_answers)
    session.setdefault("assessment_results", {})[assessment_id] = result
    flash(f"Assessment submitted: {result['percentage']}% ({'Pass' if result['passed'] else 'Fail'})", "success")
    return redirect(url_for("trainee.dashboard"))
