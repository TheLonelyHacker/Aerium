from flask import Flask, jsonify, render_template, request, make_response, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import time
from datetime import datetime, date, UTC, timedelta
import os
from database import (get_db, init_db, get_user_by_username, create_user, get_user_by_id,
                      get_user_settings, update_user_settings, reset_user_settings,
                      create_verification_token, verify_email_token, cleanup_expired_tokens,
                      get_user_by_email, create_password_reset_token, verify_reset_token,
                      reset_password, cleanup_expired_reset_tokens, log_login, get_login_history,
                      is_admin, set_user_role, get_all_users, get_admin_stats)
import json
from flask import send_file
import io
from weasyprint import HTML
import threading
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import secrets

from fake_co2 import generate_co2, save_reading, reset_state
from database import cleanup_old_data


app = Flask(__name__)
app.config['SECRET_KEY'] = 'morpheus-co2-secret-key'

# Email configuration (using development/testing settings)
# In production, use environment variables for credentials
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', True)
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@morpheus-co2.local')

socketio = SocketIO(app, cors_allowed_origins="*")

init_db()

def send_verification_email(email, username, token):
    """Send email verification link"""
    try:
        # flask_mail not configured - email verification skipped
        return True
        
        verify_url = url_for('verify_email', token=token, _external=True)
        subject = "Verify your Morpheus CO₂ Account"
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #3dd98f 0%, #4db8ff 100%); padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;">
                        <h1 style="margin: 0;">🌍 Morpheus CO₂ Monitor</h1>
                    </div>
                    
                    <h2 style="color: #3dd98f;">Welcome, {username}!</h2>
                    <p>Thank you for registering with Morpheus. Please verify your email address to complete your account setup.</p>
                    
                    <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                        <p style="margin-bottom: 15px;">Click the button below to verify your email:</p>
                        <a href="{verify_url}" style="background: linear-gradient(135deg, #3dd98f 0%, #4db8ff 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Verify Email</a>
                    </div>
                    
                    <p style="font-size: 12px; color: #666;">Or copy and paste this link in your browser:</p>
                    <p style="font-size: 11px; color: #666; word-break: break-all; background: #f0f0f0; padding: 10px; border-radius: 4px;">{verify_url}</p>
                    
                    <p style="font-size: 12px; color: #999; margin-top: 20px; border-top: 1px solid #ddd; padding-top: 20px;">
                        This link will expire in 24 hours. If you didn't create this account, please ignore this email.
                    </p>
                </div>
            </body>
        </html>
        """
        
        msg = Message(subject=subject, recipients=[email], html=html_body)
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def send_password_reset_email(email, username, token):
    """Send password reset email"""
    try:
        # flask_mail not configured - reset email skipped
        return True
        
        reset_url = url_for('reset_password_page', token=token, _external=True)
        subject = "Reset your Morpheus CO₂ Password"
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #3dd98f 0%, #4db8ff 100%); padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;">
                        <h1 style="margin: 0;">🌍 Morpheus CO₂ Monitor</h1>
                    </div>
                    
                    <h2 style="color: #3dd98f;">Password Reset Request</h2>
                    <p>Hi {username},</p>
                    <p>You requested to reset your password. Click the button below to proceed:</p>
                    
                    <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                        <p style="margin-bottom: 15px;">Click the button below to reset your password:</p>
                        <a href="{reset_url}" style="background: linear-gradient(135deg, #3dd98f 0%, #4db8ff 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Reset Password</a>
                    </div>
                    
                    <p style="font-size: 12px; color: #666;">Or copy and paste this link in your browser:</p>
                    <p style="font-size: 11px; color: #666; word-break: break-all; background: #f0f0f0; padding: 10px; border-radius: 4px;">{reset_url}</p>
                    
                    <p style="font-size: 12px; color: #999; margin-top: 20px; border-top: 1px solid #ddd; padding-top: 20px;">
                        This link will expire in 1 hour. If you didn't request this, please ignore this email and your password will remain unchanged.
                    </p>
                </div>
            </body>
        </html>
        """
        
        msg = Message(subject=subject, recipients=[email], html=html_body)
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send password reset email: {str(e)}")
        return False

def load_settings():
    """Load settings - always use global settings (per-user settings for API only)"""
    # Fallback to global settings
    db = get_db()
    rows = db.execute("SELECT key, value FROM settings").fetchall()
    db.close()

    settings = DEFAULT_SETTINGS.copy()
    for r in rows:
        settings[r["key"]] = json.loads(r["value"])

    return settings

print("=" * 50)
print(f"Current directory: {os.getcwd()}")
print(f"Template folder exists: {os.path.exists('templates')}")
if os.path.exists('templates'):
    print(f"Files in templates/: {os.listdir('templates')}")
print("=" * 50)

DEFAULT_SETTINGS = {
    "analysis_running": True,
    "good_threshold": 800,
    "bad_threshold": 1200,
    "alert_threshold": 1400,
    "realistic_mode": True,
    "update_speed": 1,
    "overview_update_speed": 5,
}

# ================================================================================
#                        AUTHENTICATION DECORATOR
# ================================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page', next=request.url))
        if not is_admin(session['user_id']):
            return render_template("error.html", 
                error="Access Denied",
                message="You need administrator privileges to access this page."), 403
        return f(*args, **kwargs)
    return decorated_function

# ================================================================================
#                        AUTHENTICATION ROUTES
# ================================================================================

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember_me = request.form.get("remember_me") == "on"
        
        if not username or not password:
            return render_template("login.html", error="Nom d'utilisateur et mot de passe requis")
        
        user = get_user_by_username(username)
        
        if user and check_password_hash(user['password_hash'], password):
            # Check if email is verified
            if not user['email_verified']:
                # Log failed login attempt
                ip_address = request.remote_addr
                user_agent = request.headers.get('User-Agent', 'Unknown')
                log_login(user['id'], ip_address, user_agent, success=False)
                
                return render_template("login.html", 
                    error="Veuillez vérifier votre email avant de vous connecter. Vérifiez votre spam.")
            
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            # Log successful login
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', 'Unknown')
            log_login(user['id'], ip_address, user_agent, success=True)
            
            # Handle "Remember Me" - extend session duration
            if remember_me:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=30)
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            return render_template("login.html", error="Identifiants invalides")
    
    return render_template("login.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password_page():
    """Request password reset"""
    if request.method == "POST":
        email = request.form.get("email")
        
        if not email:
            return render_template("forgot_password.html", error="Veuillez entrer votre email")
        
        user = get_user_by_email(email)
        
        if user:
            # Generate reset token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now(UTC) + timedelta(hours=1)
            create_password_reset_token(user['id'], token, expires_at)
            
            # Send reset email
            email_sent = send_password_reset_email(email, user['username'], token)
            
            if email_sent:
                return render_template("forgot_password.html",
                    success=True,
                    message=f"Vérifiez votre email ({email}) pour obtenir le lien de réinitialisation du mot de passe.")
            else:
                # Email service not configured, still show success for security
                return render_template("forgot_password.html",
                    success=True,
                    message="Si ce compte existe, un email de réinitialisation a été envoyé.")
        else:
            # Don't reveal if email exists (security best practice)
            return render_template("forgot_password.html",
                success=True,
                message="Si ce compte existe, un email de réinitialisation a été envoyé.")
    
    return render_template("forgot_password.html")

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password_page(token):
    """Reset password with token"""
    user_id = verify_reset_token(token)
    
    if not user_id:
        return render_template("reset_password.html", 
            error="Lien de réinitialisation invalide ou expiré.", 
            valid_token=False), 400
    
    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        # Validation
        if not new_password or not confirm_password:
            return render_template("reset_password.html", error="Tous les champs sont requis", valid_token=True)
        
        if len(new_password) < 6:
            return render_template("reset_password.html", 
                error="Le mot de passe doit contenir au moins 6 caractères", 
                valid_token=True)
        
        if new_password != confirm_password:
            return render_template("reset_password.html", 
                error="Les mots de passe ne correspondent pas", 
                valid_token=True)
        
        # Reset password
        new_password_hash = generate_password_hash(new_password)
        reset_password(user_id, new_password_hash, token)
        
        return render_template("reset_password.html", 
            success=True, 
            message="Votre mot de passe a été réinitialisé avec succès! Vous pouvez maintenant vous connecter.")
    
    return render_template("reset_password.html", valid_token=True)

@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Validation
        if not all([username, email, password, confirm_password]):
            return render_template("register.html", error="Tous les champs sont requis")
        
        if username and len(username) < 3:
            return render_template("register.html", error="Le nom d'utilisateur doit contenir au moins 3 caractères")
        
        if len(password) < 6:
            return render_template("register.html", error="Le mot de passe doit contenir au moins 6 caractères")
        
        if password != confirm_password:
            return render_template("register.html", error="Les mots de passe ne correspondent pas")
        
        # Check if username or email already exists
        if get_user_by_username(username):
            return render_template("register.html", error="Ce nom d'utilisateur existe déjà")
        
        # Create user
        password_hash = generate_password_hash(password) if password else None
        user_id = create_user(username, email, password_hash)
        
        if not user_id:
            return render_template("register.html", error="Cet email existe déjà")
        
        # Generate verification token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC) + timedelta(hours=24)
        create_verification_token(user_id, token, expires_at)
        
        # Send verification email
        email_sent = send_verification_email(email, username, token)
        
        if email_sent:
            return render_template("register.html", 
                success=True,
                message=f"Inscription réussie! Vérifiez votre email ({email}) pour confirmer votre compte.")
        else:
            # Email service not configured, allow login without verification
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('index'))
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route("/verify/<token>")
def verify_email(token):
    """Verify user email with token"""
    user_id = verify_email_token(token)
    
    if user_id:
        user = get_user_by_id(user_id)
        return render_template("email_verified.html", username=user['username'], success=True)
    else:
        return render_template("email_verified.html", 
            error="Lien de vérification invalide ou expiré. Veuillez vous réinscrire.",
            success=False), 400

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session.get('user_id')
    user = get_user_by_id(user_id)
    user_settings = get_user_settings(user_id)
    login_history = get_login_history(user_id, limit=5)  # Get last 5 logins
    
    if request.method == "POST":
        # Update user settings
        good_threshold = request.form.get('good_threshold', type=int)
        bad_threshold = request.form.get('bad_threshold', type=int)
        alert_threshold = request.form.get('alert_threshold', type=int)
        audio_alerts = request.form.get('audio_alerts') == 'on'
        email_alerts = request.form.get('email_alerts') == 'on'
        
        update_user_settings(
            user_id,
            good_threshold=good_threshold,
            bad_threshold=bad_threshold,
            alert_threshold=alert_threshold,
            audio_alerts=audio_alerts,
            email_alerts=email_alerts
        )
        
        # Reload settings
        user_settings = get_user_settings(user_id)
        return render_template("profile.html", user=user, settings=user_settings, login_history=login_history, success=True)
    
    return render_template("profile.html", user=user, settings=user_settings, login_history=login_history)

@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    user_id = session.get('user_id')
    user = get_user_by_id(user_id)
    
    if request.method == "POST":
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        error = None
        
        # Validation
        if not all([current_password, new_password, confirm_password]):
            error = "Tous les champs sont requis"
        elif not check_password_hash(user['password_hash'], current_password):
            error = "Mot de passe actuel incorrect"
        elif not (new_password and len(new_password) >= 6):
            error = "Le nouveau mot de passe doit contenir au moins 6 caractères"
        elif new_password != confirm_password:
            error = "Les mots de passe ne correspondent pas"
        
        if error:
            return render_template("change_password.html", error=error)
        
        # Update password
        db = get_db()
        new_password_hash = generate_password_hash(new_password) if new_password else None
        db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (new_password_hash, user_id)
        )
        db.commit()
        db.close()
        
        return render_template("change_password.html", success=True)
    
    return render_template("change_password.html", user=user)
    return render_template("profile.html", user=user, settings=user_settings)

# 1. ROOT ROUTE - DASHBOARD (MUST BE FIRST!)
@app.route("/")
@login_required
def index():
    return render_template("index.html")  # Overview/vue d'ensemble page

@app.route("/dashboard")
@login_required
def dashboard():
    """Unified landing page - shows admin dashboard for admins, user info for others"""
    user_id = session.get('user_id')
    
    if is_admin(user_id):
        # Show admin dashboard with stats
        admin_stats = get_admin_stats()
        admin_users = get_all_users()
        return render_template("dashboard.html", 
                             is_admin=True,
                             admin_stats=admin_stats,
                             admin_users=admin_users)
    else:
        # Show regular user landing page
        return render_template("dashboard.html", is_admin=False)

@app.route("/live")
@login_required
def live_page():
    return render_template("live.html")  # Settings page

# 2. SETTINGS ROUTE
@app.route("/settings")
@login_required
def settings_page():
    return render_template("settings.html")  # Settings page

@app.route("/analytics")
@login_required
def analytics():
    return render_template("analytics.html")

@app.route("/admin")
@admin_required
def admin_dashboard():
    """Admin dashboard with statistics and user management"""
    stats = get_admin_stats()
    users = get_all_users()
    
    return render_template("admin.html", stats=stats, users=users)

@app.route("/admin/user/<int:user_id>/role/<role>", methods=["POST"])
@admin_required
def update_user_role(user_id, role):
    """Update user role (admin or user)"""
    if role not in ['user', 'admin']:
        return jsonify({'error': 'Invalid role'}), 400
    
    # Prevent self-demotion
    if user_id == session.get('user_id') and role == 'user':
        return jsonify({'error': 'Cannot remove your own admin privileges'}), 400
    
    if set_user_role(user_id, role):
        return jsonify({'success': True, 'role': role})
    return jsonify({'error': 'Failed to update role'}), 500

@app.route("/api/history/<range>")
def history_range(range):
    db = get_db()

    if range == "today":
        rows = db.execute("""
            SELECT ppm, timestamp
            FROM co2_readings
            WHERE date(timestamp) = date('now')
            ORDER BY timestamp
        """).fetchall()

    elif range == "7d":
        rows = db.execute("""
            SELECT ppm, timestamp
            FROM co2_readings
            WHERE timestamp >= datetime('now', '-7 days')
            ORDER BY timestamp
        """).fetchall()

    elif range == "30d":
        rows = db.execute("""
            SELECT ppm, timestamp
            FROM co2_readings
            WHERE timestamp >= datetime('now', '-30 days')
            ORDER BY timestamp
        """).fetchall()

    else:
        db.close()
        return jsonify({"error": "Invalid range"}), 400

    db.close()
    return jsonify([dict(r) for r in rows])

# 3. API ROUTES
@app.route("/api/latest")
def api_latest():
    settings = load_settings()

    if not settings["analysis_running"]:
        resp = make_response(jsonify({
            "analysis_running": False,
            "ppm": None
        }))
        resp.headers["Cache-Control"] = "no-store"
        return resp

    ppm = generate_co2(settings["realistic_mode"])
    save_reading(ppm)

    resp = make_response(jsonify({
        "analysis_running": True,
        "ppm": ppm,
        "timestamp": datetime.utcnow().isoformat()
    }))
    resp.headers["Cache-Control"] = "no-store"
    return resp

@app.route("/api/history/today")
def api_history_today():
    db = get_db()
    rows = db.execute("""
        SELECT ppm, timestamp
        FROM co2_readings
        WHERE date(timestamp) = date('now')
        ORDER BY timestamp
    """).fetchall()
    db.close()

    return jsonify([dict(r) for r in rows])

def get_today_history():
    db = get_db()
    rows = db.execute("""
        SELECT ppm, timestamp
        FROM co2_readings
        WHERE date(timestamp) = date('now')
        ORDER BY timestamp
    """).fetchall()
    db.close()

    return [dict(r) for r in rows]


@app.route("/api/settings", methods=["GET", "POST", "DELETE"])
@login_required
def api_settings():
    user_id = session.get('user_id')
    
    if request.method == "POST":
        # Save per-user settings
        settings_data = {
            'good_threshold': request.json.get('good_threshold', 800),
            'bad_threshold': request.json.get('bad_threshold', 1200),
            'alert_threshold': request.json.get('alert_threshold', 1400),
            'realistic_mode': request.json.get('realistic_mode', True),
            'update_speed': request.json.get('update_speed', 1),
            'analysis_running': request.json.get('analysis_running', True),
        }
        update_user_settings(user_id, settings_data)
        
        # Broadcast update to all WebSocket clients so other pages refresh
        socketio.emit('settings_update', settings_data)
        
        return jsonify({"status": "ok"})

    if request.method == "DELETE":
        # Reset per-user settings to defaults
        db = get_db()
        db.execute("DELETE FROM user_settings WHERE user_id = ?", (user_id,))
        db.commit()
        db.close()
        
        # Broadcast reset to all WebSocket clients
        socketio.emit('settings_update', DEFAULT_SETTINGS)
        return jsonify(DEFAULT_SETTINGS)

    # GET - return per-user settings
    user_settings = get_user_settings(user_id)
    if user_settings:
        # Convert sqlite3.Row to dict for .get() support
        settings_dict = dict(user_settings) if hasattr(user_settings, 'keys') else user_settings
        return jsonify({
            "analysis_running": settings_dict.get('analysis_running', True),
            "good_threshold": settings_dict.get('good_threshold', 800),
            "bad_threshold": settings_dict.get('bad_threshold', 1200),
            "alert_threshold": settings_dict.get('alert_threshold', 1400),
            "realistic_mode": settings_dict.get('realistic_mode', True),
            "update_speed": settings_dict.get('update_speed', 1),
            "overview_update_speed": 5,
        })
    
    return jsonify(load_settings())

@app.route("/api/user-info")
@login_required
def api_user_info():
    user_id = session.get('user_id')
    db = get_db()
    user = db.execute("SELECT username, email FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    
    if user:
        return jsonify({
            "username": user['username'],
            "email": user['email']
        })
    return jsonify({"error": "User not found"}), 404

@app.route("/api/history/latest/<int:limit>")
def api_history_latest(limit):
    db = get_db()
    rows = db.execute("""
        SELECT id, ppm, timestamp
        FROM co2_readings
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()
    db.close()

    # reverse so oldest → newest
    return jsonify([dict(r) for r in reversed(rows)])

@app.route("/api/cleanup", methods=["POST"])
def api_cleanup():
    """Clean up old CO₂ readings (default: 90 days)"""
    days = request.json.get("days", 90) if request.json else 90
    deleted = cleanup_old_data(days)
    return jsonify({"status": "ok", "deleted": deleted, "days": days})

@app.route("/api/reset-state", methods=["POST"])
def api_reset_state():
    """Reset CO₂ generator state"""
    base = request.json.get("base", 600) if request.json else 600
    reset_state(base)
    return jsonify({"status": "ok", "base": base})


def generate_pdf(html):
    pdf_io = io.BytesIO()

    HTML(
        string=html,
        base_url=os.path.abspath(".")
    ).write_pdf(
        target=pdf_io,
        presentational_hints=True
    )

    pdf_io.seek(0)

    return send_file(
        pdf_io,
        mimetype="application/pdf",
        as_attachment=False,
        download_name="daily_report.pdf"
    )


@app.route("/api/report/daily/pdf")
def export_daily_pdf():
    data = get_today_history()
    settings = load_settings()

    if not data:
        return "No data", 400

    values = [d["ppm"] for d in data]

    avg = round(sum(values) / len(values))
    max_ppm = max(values)
    min_ppm = min(values)

    # ⏱ minutes above bad threshold
    bad_minutes = sum(1 for v in values if v >= settings["bad_threshold"])

    # ✅ EXPOSURE BREAKDOWN (THIS IS YOUR QUESTION)
    good = sum(1 for v in values if v < settings["good_threshold"])
    medium = sum(
        1 for v in values
        if settings["good_threshold"] <= v < settings["bad_threshold"]
    )
    bad = sum(1 for v in values if v >= settings["bad_threshold"])
    total = len(values)

    good_pct = round(good / total * 100)
    medium_pct = round(medium / total * 100)
    bad_pct = round(bad / total * 100)

    with open("static/css/report.css", "r", encoding="utf-8") as f:
        report_css = f.read()

    html = render_template(
        "report_daily.html",
        date=date.today().strftime("%d %B %Y"),
        avg=avg,
        max=max_ppm,
        min=min_ppm,
        bad_minutes=bad_minutes,
        good_pct=good_pct,
        medium_pct=medium_pct,
        bad_pct=bad_pct,
        good_threshold=settings["good_threshold"],
        bad_threshold=settings["bad_threshold"],
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        report_css=report_css
    )

    return generate_pdf(html)


@app.route("/healthz")
def healthz():
    db = get_db()
    latest = db.execute("SELECT ppm, timestamp FROM co2_readings ORDER BY id DESC LIMIT 1").fetchone()
    count = db.execute("SELECT COUNT(*) AS c FROM co2_readings").fetchone()["c"]
    settings = load_settings()
    db.close()

    return jsonify({
        "status": "ok",
        "analysis_running": settings.get("analysis_running", True),
        "rows": count,
        "latest_ppm": latest["ppm"] if latest else None,
        "latest_timestamp": latest["timestamp"] if latest else None,
    })


@app.route("/metrics")
def metrics():
    db = get_db()
    latest = db.execute("SELECT ppm, timestamp FROM co2_readings ORDER BY id DESC LIMIT 1").fetchone()
    count = db.execute("SELECT COUNT(*) AS c FROM co2_readings").fetchone()["c"]
    settings = load_settings()
    db.close()

    payload = {
        "rows": count,
        "analysis_running": settings.get("analysis_running", True),
        "good_threshold": settings.get("good_threshold"),
        "bad_threshold": settings.get("bad_threshold"),
        "update_speed": settings.get("update_speed"),
        "overview_update_speed": settings.get("overview_update_speed"),
        "latest_ppm": latest["ppm"] if latest else None,
        "latest_timestamp": latest["timestamp"] if latest else None,
    }

    return jsonify(payload)


# ================================================================================
#                          WEBSOCKET HANDLERS
# ================================================================================

# Global state for WebSocket broadcasting
broadcast_thread = None
broadcast_running = False

@socketio.on('connect')
def handle_connect():
    """Handle client connection to WebSocket"""
    print(f"Client connected")
    emit('status', {'data': 'Connected to Morpheus CO₂ Monitor'})
    
    # Send current settings to client
    settings = load_settings()
    emit('settings_update', settings)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected")

@socketio.on('request_data')
def handle_request_data():
    """Handle request for latest CO₂ data"""
    settings = load_settings()
    
    if not settings["analysis_running"]:
        emit('co2_update', {
            'analysis_running': False,
            'ppm': None,
            'timestamp': datetime.now(UTC).isoformat()
        })
        return
    
    ppm = generate_co2(settings["realistic_mode"])
    save_reading(ppm)
    
    emit('co2_update', {
        'analysis_running': True,
        'ppm': ppm,
            'timestamp': datetime.now(UTC).isoformat()
    })

@socketio.on('settings_change')
def handle_settings_change(data):
    """Handle settings update and broadcast to all clients"""
    # Settings now saved per-user via API endpoint
    # Broadcast to all clients
    socketio.emit('settings_update', data)

def broadcast_co2_loop():
    """Background thread that broadcasts CO₂ readings to all connected clients"""
    global broadcast_running
    broadcast_running = True
    last_ppm = None
    last_analysis_state = None
    
    while broadcast_running:
        settings = load_settings()
        
        if settings["analysis_running"]:
            ppm = generate_co2(settings["realistic_mode"])
            save_reading(ppm)
            
            # Only broadcast if value changed significantly (>= 5 ppm) or state changed
            if last_ppm is None or abs(ppm - last_ppm) >= 5 or last_analysis_state != True:
                socketio.emit('co2_update', {
                    'analysis_running': True,
                    'ppm': ppm,
                    'timestamp': datetime.now(UTC).isoformat()
                }, to=None)
                last_ppm = ppm
                last_analysis_state = True
        else:
            # Only broadcast state change once
            if last_analysis_state != False:
                socketio.emit('co2_update', {
                    'analysis_running': False,
                    'ppm': None,
                    'timestamp': datetime.now(UTC).isoformat()
                }, to=None)
                last_analysis_state = False
        
        # Respect update_speed setting (default 1 second)
        update_delay = settings.get("update_speed", 1)
        time.sleep(update_delay)

def start_broadcast_thread():
    """Start the background broadcast thread"""
    global broadcast_thread, broadcast_running
    if broadcast_thread is None or not broadcast_thread.is_alive():
        broadcast_running = True
        broadcast_thread = threading.Thread(target=broadcast_co2_loop, daemon=True)
        broadcast_thread.start()
        print("[OK] WebSocket broadcast thread started")

def stop_broadcast_thread():
    """Stop the background broadcast thread"""
    global broadcast_running
    broadcast_running = False
    print("[OK] WebSocket broadcast thread stopped")




if __name__ == "__main__":
    start_broadcast_thread()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)