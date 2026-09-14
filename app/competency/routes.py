from flask import Blueprint, render_template

competency_bp = Blueprint("competency", __name__)


def match_trainer_for_trainee(trainee_skills, trainers):
    recommendations = []
    ordered_required_skills = [skill.strip() for skill in trainee_skills if skill and skill.strip()]
    normalized_trainee_skills = {skill.lower() for skill in ordered_required_skills}

    for trainer in trainers:
        trainer_skills = trainer.get("skills", [])
        trainer_skill_lookup = {skill.strip().lower() for skill in trainer_skills if skill and skill.strip()}
        matched_skills = [
            skill
            for skill in ordered_required_skills
            if skill.lower() in trainer_skill_lookup
        ]

        total_required = len(normalized_trainee_skills)
        if total_required == 0:
            match_percentage = 0
        else:
            match_percentage = round((len(matched_skills) / total_required) * 100)

        recommendations.append(
            {
                "name": trainer.get("name", "Unknown Trainer"),
                "expertise": trainer.get("expertise", "General expertise"),
                "match": match_percentage,
                "matched_skills": matched_skills,
                "subjects": matched_skills,
            }
        )

    return sorted(recommendations, key=lambda item: item["match"], reverse=True)


@competency_bp.route("/")
def index():
    trainee_skills = ["Python", "Data Analysis"]
    trainers = [
        {"name": "Dr. Ananya Raman", "expertise": "Python, Data Analysis, Machine Learning", "skills": ["Python", "Data Analysis", "Machine Learning"]},
        {"name": "Mr. Sandeep Iyer", "expertise": "Climate Modelling, Data Storytelling", "skills": ["Python", "Climate Modelling"]},
    ]
    recommendations = match_trainer_for_trainee(trainee_skills, trainers)
    return render_template("competency.html", recommendations=recommendations)
