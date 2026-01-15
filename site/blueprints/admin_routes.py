from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for
from utils.auth_decorators import login_required, admin_required
from database import (
    get_user_by_id,
    get_admin_stats,
    get_all_users,
    get_audit_logs,
    get_database_info,
    set_user_role,
    delete_user_with_audit,
    cleanup_old_data,
    cleanup_old_audit_logs,
    cleanup_old_login_history,
    log_audit,
    is_admin,
)

admin_bp = Blueprint("admin_routes", __name__)


@admin_bp.route("/admin-tools")
@login_required
def admin_tools():
    """Advanced admin tools - Audit logs, sessions, retention, backups"""
    user = get_user_by_id(session.get("user_id"))
    if not user or user["role"] != "admin":
        return redirect(url_for("main.dashboard"))
    return render_template("admin/admin-tools.html")


@admin_bp.route("/debug-session")
def debug_session():
    """Debug session and auth info"""
    user_data = None
    if session.get("user_id"):
        user = get_user_by_id(session.get("user_id"))
        if user:
            user_data = {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"],
            }

    return jsonify(
        {
            "session_user_id": session.get("user_id"),
            "session_username": session.get("username"),
            "user_in_session": "user_id" in session,
            "is_admin_result": is_admin(session.get("user_id")) if "user_id" in session else None,
            "user_data": user_data,
        }
    )


@admin_bp.route("/admin")
@admin_required
def admin_dashboard():
    """Admin dashboard with statistics and user management"""
    stats = get_admin_stats()
    users = get_all_users()
    audit_logs = get_audit_logs(limit=20)
    db_info = get_database_info()

    return render_template(
        "admin/admin.html",
        stats=stats,
        users=users,
        audit_logs=audit_logs,
        db_info=db_info,
    )


@admin_bp.route("/admin/user/<int:user_id>/role/<role>", methods=["POST"])
@admin_required
def update_user_role(user_id, role):
    """Update user role (admin or user)"""
    if role not in ["user", "admin"]:
        return jsonify({"error": "Invalid role"}), 400

    # Prevent self-demotion
    if user_id == session.get("user_id") and role == "user":
        return jsonify({"error": "Cannot remove your own admin privileges"}), 400

    if set_user_role(user_id, role):
        admin_id = session.get("user_id")
        ip_address = request.remote_addr
        log_audit(admin_id, "user_role_updated", "user", user_id, "role_changed", f"user → {role}", ip_address)
        return jsonify({"success": True, "role": role})
    return jsonify({"error": "Failed to update role"}), 500


@admin_bp.route("/api/permissions", methods=["GET"])
@login_required
def get_my_permissions():
    """Get current user's permissions"""
    from database import get_user_permissions

    user_id = session.get("user_id")
    permissions = get_user_permissions(user_id)
    return jsonify({"permissions": permissions})


@admin_bp.route("/api/permissions/<int:user_id>", methods=["GET"])
@admin_required
def get_user_perms(user_id):
    """Get a specific user's permissions (admin only)"""
    from database import get_user_permissions

    permissions = get_user_permissions(user_id)
    return jsonify({"user_id": user_id, "permissions": permissions})


@admin_bp.route("/api/permissions/<int:user_id>/<permission>", methods=["POST"])
@admin_required
def add_permission(user_id, permission):
    """Grant a permission to a user"""
    from database import grant_permission

    valid_perms = ["view_reports", "manage_exports", "manage_sensors", "manage_alerts", "manage_users"]

    if permission not in valid_perms:
        return jsonify({"error": f"Invalid permission. Valid: {', '.join(valid_perms)}"}), 400

    grant_permission(user_id, permission)
    log_audit(
        session.get("user_id"),
        "permission_granted",
        "user",
        user_id,
        "permission",
        permission,
        request.remote_addr,
    )

    return jsonify({"status": "ok", "permission": permission})


@admin_bp.route("/api/permissions/<int:user_id>/<permission>", methods=["DELETE"])
@admin_required
def remove_permission(user_id, permission):
    """Revoke a permission from a user"""
    from database import revoke_permission

    revoke_permission(user_id, permission)
    log_audit(
        session.get("user_id"),
        "permission_revoked",
        "user",
        user_id,
        "permission",
        permission,
        request.remote_addr,
    )

    return jsonify({"status": "ok", "permission": permission})


@admin_bp.route("/admin/user/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user_admin(user_id):
    """Delete a user account (admin only)"""
    if user_id == session.get("user_id"):
        return jsonify({"error": "Cannot delete your own account"}), 400

    admin_id = session.get("user_id")
    ip_address = request.remote_addr

    if delete_user_with_audit(user_id, admin_id, ip_address):
        return jsonify({"success": True})

    return jsonify({"error": "Failed to delete user"}), 500


@admin_bp.route("/admin/maintenance", methods=["POST"])
@admin_required
def admin_maintenance():
    """Execute maintenance tasks"""
    payload = request.get_json() or {}
    task = payload.get("task")
    admin_id = session.get("user_id")
    ip_address = request.remote_addr

    results = {}

    if task == "cleanup_old_data":
        days = payload.get("days", 90)
        deleted = cleanup_old_data(days)
        results["deleted_readings"] = deleted
        log_audit(admin_id, "maintenance_cleanup_data", None, None, f"days={days}", f"deleted={deleted}", ip_address)

    elif task == "cleanup_old_logs":
        days = payload.get("days", 180)
        deleted = cleanup_old_audit_logs(days)
        results["deleted_audit_logs"] = deleted
        log_audit(admin_id, "maintenance_cleanup_logs", None, None, f"days={days}", f"deleted={deleted}", ip_address)

    elif task == "cleanup_login_history":
        days = payload.get("days", 90)
        deleted = cleanup_old_login_history(days)
        results["deleted_logins"] = deleted
        log_audit(admin_id, "maintenance_cleanup_logins", None, None, f"days={days}", f"deleted={deleted}", ip_address)

    else:
        return jsonify({"error": "Unknown maintenance task"}), 400

    return jsonify({"success": True, **results})


@admin_bp.route("/api/admin/database-info")
@login_required
def api_database_info():
    """Get database information (admin only)"""
    user_id = session["user_id"]

    if not is_admin(user_id):
        return jsonify({"error": "Admin access required"}), 403

    try:
        import os
        import sqlite3
        from pathlib import Path

        main_db_path = Path("../data/aerium.sqlite")
        site_db_path = Path("data/aerium.sqlite")
        db_path = str(main_db_path if main_db_path.exists() else site_db_path)

        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            modified = os.path.getmtime(db_path)
        else:
            return jsonify({"error": "Database file not found"}), 404

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        schema_str = "Tables:\n"
        for table in tables:
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                schema_str += f"\n{table}:\n"
                for col in columns:
                    schema_str += f"  - {col[1]} ({col[2]})\n"
            except sqlite3.OperationalError:
                schema_str += f"\n{table}: [Error reading schema]\n"

        conn.close()

        return jsonify({
            "file": db_path,
            "size": size,
            "modified": modified,
            "tables": tables,
            "schema": schema_str,
        })
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@admin_bp.route("/api/admin/backup-database", methods=["POST"])
@login_required
def api_backup_database():
    """Create database backup (admin only)"""
    user_id = session["user_id"]

    if not is_admin(user_id):
        return jsonify({"error": "Admin access required"}), 403

    try:
        import os
        import shutil
        from datetime import datetime
        from pathlib import Path
        from flask import send_file

        main_db_path = Path("../data/aerium.sqlite")
        site_db_path = Path("data/aerium.sqlite")
        db_path = str(main_db_path if main_db_path.exists() else site_db_path)

        if not os.path.exists(db_path):
            return jsonify({"error": "Database file not found"}), 404

        backup_dir = os.path.dirname(db_path) + "/backups"
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"aerium_backup_{timestamp}.sqlite"
        backup_path = os.path.join(backup_dir, backup_filename)

        shutil.copy2(db_path, backup_path)
        log_audit(user_id, "BACKUP", f"Database backed up to {backup_path}")

        return send_file(backup_path, as_attachment=True, download_name=f"aerium-backup-{timestamp}.sqlite")
    except Exception as e:
        log_audit(user_id, "ERROR", f"Backup failed: {str(e)}")
        return jsonify({"error": str(e)}), 500
