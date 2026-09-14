from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from supabase import create_client

from app import login_required

auth_bp = Blueprint("auth", __name__)

DEMO_USERS = {
    "trainee@capacityconnect.in": {"role": "trainee", "name": "Priya Reddy"},
    "trainer@capacityconnect.in": {"role": "trainer", "name": "Dr. Ananya Raman"},
    "admin@capacityconnect.in": {"role": "admin", "name": "Rakesh Sinha"},
}


def get_supabase_client(use_service_role=False):
    url = current_app.config.get("SUPABASE_URL")
    if use_service_role:
        key = (
            current_app.config.get("SUPABASE_SERVICE_ROLE_KEY")
            or current_app.config.get("SUPABASE_SECRET_KEY")
        )
    else:
        key = (
            current_app.config.get("SUPABASE_ANON_KEY")
            or current_app.config.get("SUPABASE_PUBLISHABLE_KEY")
        )

    if not url or not key:
        return None

    try:
        return create_client(url, key)
    except Exception:
        return None


def get_role_dashboard(role):
    if role == "trainee":
        return url_for("trainee.dashboard")
    if role == "trainer":
        return url_for("trainer.dashboard")
    return url_for("admin.dashboard")


def sync_profile_with_supabase(supabase, user, role_hint=None, full_name_hint=None):
    if user is None:
        return {"role": role_hint or "trainee", "name": full_name_hint or "User"}

    metadata = getattr(user, "user_metadata", {}) or {}
    resolved_role = role_hint or metadata.get("role") or "trainee"
    resolved_name = full_name_hint or metadata.get("full_name") or getattr(user, "email", "User")

    profile_payload = {
        "id": getattr(user, "id", None),
        "email": getattr(user, "email", ""),
        "full_name": resolved_name,
        "role": resolved_role,
        "phone": "",
        "profile_photo_url": None,
    }

    try:
        profile_response = supabase.table("profiles").select("id, role, full_name, email").eq("id", user.id).limit(1).execute()
        if not getattr(profile_response, "data", None):
            admin_supabase = get_supabase_client(use_service_role=True) or supabase
            admin_supabase.table("profiles").upsert(profile_payload).execute()
        else:
            existing_profile = profile_response.data[0]
            resolved_role = existing_profile.get("role") or resolved_role
            resolved_name = existing_profile.get("full_name") or resolved_name
            profile_payload["role"] = resolved_role
            profile_payload["full_name"] = resolved_name
            admin_supabase = get_supabase_client(use_service_role=True) or supabase
            admin_supabase.table("profiles").upsert(profile_payload).execute()
    except Exception:
        pass

    return {"role": resolved_role, "name": resolved_name}


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user"):
        user = session["user"]
        return redirect(get_role_dashboard(user.get("role", "trainee")))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        selected_role = request.form.get("role")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("login.html")

        demo_user = DEMO_USERS.get(email)
        if demo_user is not None:
            if password != "password123":
                flash("Invalid credentials. Use the demo account for the selected role.", "danger")
                return render_template("login.html")
            if selected_role and demo_user["role"] != selected_role:
                flash("Selected role does not match the demo account.", "warning")
                return render_template("login.html")

            session["user"] = {"email": email, "role": demo_user["role"], "name": demo_user["name"]}
            flash("Demo login successful.", "success")
            return redirect(get_role_dashboard(demo_user["role"]))

        supabase = get_supabase_client()
        if supabase is not None:
            try:
                auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                user = getattr(auth_response, "user", None)
                if user is None:
                    flash("Unable to sign in. Please verify your Supabase credentials.", "danger")
                    return render_template("login.html")

                profile = sync_profile_with_supabase(supabase, user, selected_role, getattr(user, "user_metadata", {}).get("full_name"))
                resolved_role = profile.get("role") or selected_role or "trainee"

                if selected_role and selected_role != resolved_role:
                    flash("Selected role does not match this account. Please choose the correct role for this user.", "warning")
                    return render_template("login.html")

                session["user"] = {
                    "email": getattr(user, "email", email),
                    "role": resolved_role,
                    "name": profile.get("name") or getattr(user, "user_metadata", {}).get("full_name") or email,
                }
                flash("Supabase login successful.", "success")
                return redirect(get_role_dashboard(resolved_role))
            except Exception as exc:
                flash(f"Supabase sign-in failed: {exc}", "danger")
                return render_template("login.html")

        flash("Supabase credentials are missing or invalid. Use the real anon/public key from Supabase Dashboard > Settings > API, or keep the demo mode fallback.", "warning")
        return render_template("login.html")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user"):
        user = session["user"]
        return redirect(get_role_dashboard(user.get("role", "trainee")))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role")

        if not full_name or not email or not password or not role:
            flash("Please complete all registration fields.", "danger")
            return render_template("register.html")

        if role == "admin":
            flash("Admin creation is restricted to secure approval workflows. Please contact the platform administrator.", "warning")
            return redirect(url_for("auth.login"))

        supabase = get_supabase_client()
        if supabase is not None:
            try:
                response = supabase.auth.sign_up(
                    {
                        "email": email,
                        "password": password,
                        "options": {"data": {"full_name": full_name, "role": role}},
                    }
                )
                user = getattr(response, "user", None)
                if user is None:
                    flash("Supabase registration did not return a user record.", "danger")
                    return render_template("register.html")

                profile_payload = {
                    "id": user.id,
                    "full_name": full_name,
                    "email": getattr(user, "email", email),
                    "role": role,
                    "phone": "",
                    "profile_photo_url": None,
                }
                try:
                    admin_supabase = get_supabase_client(use_service_role=True) or supabase
                    admin_supabase.table("profiles").upsert(profile_payload).execute()
                except Exception as exc:
                    flash(f"Account created, but profile sync needs attention: {exc}", "warning")

                flash("Account created successfully through Supabase Auth.", "success")
                return redirect(url_for("auth.login"))
            except Exception as exc:
                flash(f"Supabase registration failed: {exc}", "danger")
                return render_template("register.html")

        flash("Supabase credentials are missing or invalid. Use the real anon/public key from Supabase Dashboard > Settings > API, or keep the demo mode fallback.", "warning")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))


@auth_bp.route("/profile")
@login_required(["trainee", "trainer", "admin"])
def profile():
    user = session.get("user")
    return render_template("profile.html", user=user)
