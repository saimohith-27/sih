from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from supabase import create_client

from app import login_required

admin_bp = Blueprint("admin", __name__)

USER_STORE = [
    {"id": 1, "name": "Priya Reddy", "email": "trainee@capacityconnect.in", "role": "trainee", "status": "Approved"},
    {"id": 2, "name": "Dr. Ananya Raman", "email": "trainer@capacityconnect.in", "role": "trainer", "status": "Approved"},
    {"id": 3, "name": "Rakesh Sinha", "email": "admin@capacityconnect.in", "role": "admin", "status": "Active"},
]


def get_supabase_client(use_service_role=False):
    url = current_app.config.get("SUPABASE_URL")
    if use_service_role:
        key = current_app.config.get("SUPABASE_SERVICE_ROLE_KEY") or current_app.config.get("SUPABASE_SECRET_KEY")
    else:
        key = current_app.config.get("SUPABASE_ANON_KEY") or current_app.config.get("SUPABASE_PUBLISHABLE_KEY")

    if not url or not key:
        return None

    try:
        return create_client(url, key)
    except Exception:
        return None


def normalize_profile_row(row):
    return {
        "id": row.get("id") or row.get("profile_id"),
        "name": row.get("full_name") or row.get("name") or row.get("email", "User"),
        "email": row.get("email") or "",
        "role": row.get("role") or "trainee",
        "status": row.get("status") or "Approved",
    }


def get_admin_users():
    supabase = get_supabase_client(use_service_role=True) or get_supabase_client()
    if supabase is not None:
        try:
            response = supabase.table("profiles").select("id, full_name, email, role, status").execute()
            rows = getattr(response, "data", None) or []
            if rows:
                return [normalize_profile_row(row) for row in rows]
        except Exception:
            pass
    return USER_STORE


@admin_bp.route("/dashboard")
@login_required("admin")
def dashboard():
    stats = {
        "total_users": len(USER_STORE),
        "trainees": sum(1 for user in USER_STORE if user["role"] == "trainee"),
        "trainers": sum(1 for user in USER_STORE if user["role"] == "trainer"),
        "courses": 31,
        "enrollments": 512,
        "certifications": 210,
        "assessments": 18,
    }
    return render_template("admin_dashboard.html", stats=stats, user=session.get("user", {}))


@admin_bp.route("/users", methods=["GET", "POST"])
@login_required("admin")
def users():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        role = request.form.get("role", "trainee")
        password = request.form.get("password", "")
        status = request.form.get("status", "Pending")

        if not name or not email or not password:
            flash("Name, email, and password are required.", "danger")
            return redirect(url_for("admin.users"))

        new_user = {
            "id": max((user["id"] for user in USER_STORE), default=0) + 1,
            "name": name,
            "email": email,
            "role": role,
            "status": status,
        }

        supabase = get_supabase_client(use_service_role=True) or get_supabase_client()
        if supabase is not None:
            profile_payload = {
                "email": email,
                "full_name": name,
                "role": role,
                "status": status,
                "phone": "",
                "profile_photo_url": None,
            }
            try:
                supabase.table("profiles").upsert(profile_payload).execute()
            except Exception as exc:
                flash(f"User record created locally, but profile sync needs attention: {exc}", "warning")

        USER_STORE.append(new_user)
        flash(f"{name} was added as a {role} without a confirmation email.", "success")
        return redirect(url_for("admin.users"))

    return render_template("admin_users.html", users=get_admin_users(), user=session.get("user", {}))


@admin_bp.route("/users/<user_id>/approve", methods=["POST"])
@login_required("admin")
def approve_user(user_id):
    candidate_id = user_id
    supabase = get_supabase_client(use_service_role=True) or get_supabase_client()
    if supabase is not None:
        try:
            update_response = supabase.table("profiles").update({"status": "Approved"}).eq("id", str(candidate_id)).execute()
            if getattr(update_response, "data", None) or getattr(update_response, "count", None):
                flash("User approved successfully.", "success")
                return redirect(url_for("admin.users"))
        except Exception:
            pass

    for user in USER_STORE:
        if str(user["id"]) == str(candidate_id):
            user["status"] = "Approved"
            flash(f"{user['name']} is now approved.", "success")
            break
    return redirect(url_for("admin.users"))


@admin_bp.route("/announcements")
@login_required("admin")
def announcements():
    return render_template("admin_announcements.html", user=session.get("user", {}))
