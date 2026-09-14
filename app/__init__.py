from functools import wraps

from flask import Flask, flash, redirect, render_template, session, url_for
from config import Config


def login_required(required_role=None):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            user = session.get("user")
            if not user:
                flash("Please log in to access that page.", "warning")
                return redirect(url_for("auth.login"))

            if required_role:
                allowed_roles = required_role if isinstance(required_role, (list, tuple, set)) else [required_role]
                if user.get("role") not in allowed_roles:
                    flash("You do not have permission to access this page.", "danger")
                    return redirect(url_for("main.home"))

            return view_func(*args, **kwargs)

        return wrapped

    return decorator


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = app.config["SECRET_KEY"]
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False

    # Register main blueprints
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.trainee.routes import trainee_bp
    from app.trainer.routes import trainer_bp
    from app.admin.routes import admin_bp
    from app.courses.routes import courses_bp
    from app.assessments.routes import assessments_bp
    from app.competency.routes import competency_bp
    from app.feedback.routes import feedback_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(trainee_bp, url_prefix="/trainee")
    app.register_blueprint(trainer_bp, url_prefix="/trainer")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(courses_bp, url_prefix="/courses")
    app.register_blueprint(assessments_bp, url_prefix="/assessments")
    app.register_blueprint(competency_bp, url_prefix="/competency")
    app.register_blueprint(feedback_bp, url_prefix="/feedback")

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("403.html"), 403

    @app.errorhandler(500)
    def server_error(error):
        return render_template("500.html"), 500

    return app
