import sqlite3
from pathlib import Path

DB_PATH = Path("data/aerium.sqlite")

def get_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    cur = db.cursor()

    # CO₂ history
    cur.execute("""
        CREATE TABLE IF NOT EXISTS co2_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ppm INTEGER NOT NULL
        )
    """)
    
    # Create index on timestamp for faster queries
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_co2_timestamp 
        ON co2_readings(timestamp DESC)
    """)
    
    # Create index on date for daily queries
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_co2_date 
        ON co2_readings(date(timestamp))
    """)

    # Settings persistence
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # Users table for authentication
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email_verified BOOLEAN DEFAULT 0,
            role TEXT DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index on username for faster lookups
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_username 
        ON users(username)
    """)

    # User settings (per-user thresholds and preferences)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            good_threshold INTEGER DEFAULT 800,
            bad_threshold INTEGER DEFAULT 1200,
            alert_threshold INTEGER DEFAULT 1400,
            realistic_mode BOOLEAN DEFAULT 1,
            update_speed INTEGER DEFAULT 1,
            audio_alerts BOOLEAN DEFAULT 1,
            email_alerts BOOLEAN DEFAULT 1,
            analysis_running BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Create index on user_id for fast lookups
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_settings_user_id 
        ON user_settings(user_id)
    """)

    # Email verification tokens (for unverified accounts)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS verification_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Create index for token lookups and cleanup
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_verification_tokens_token 
        ON verification_tokens(token)
    """)
    
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_verification_tokens_user_id 
        ON verification_tokens(user_id)
    """)

    # Password reset tokens (for forgot password feature)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Create index for reset token lookups and cleanup
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token 
        ON password_reset_tokens(token)
    """)
    
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id 
        ON password_reset_tokens(user_id)
    """)

    # Login history tracking
    cur.execute("""
        CREATE TABLE IF NOT EXISTS login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            success BOOLEAN DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Create indexes for login history
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_login_history_user_id 
        ON login_history(user_id)
    """)
    
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_login_history_time 
        ON login_history(login_time DESC)
    """)

    db.commit()
    db.close()

def cleanup_old_data(days_to_keep=90):
    """Remove CO₂ readings older than specified days (default 90 days)"""
    db = get_db()
    cur = db.cursor()
    
    cur.execute("""
        DELETE FROM co2_readings 
        WHERE timestamp < datetime('now', '-' || ? || ' days')
    """, (days_to_keep,))
    
    deleted_count = cur.rowcount
    db.commit()
    db.close()
    
    return deleted_count
# ================================================================================
#                        USER AUTHENTICATION
# ================================================================================

def get_user_by_username(username):
    """Get user by username"""
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    db.close()
    return user

def get_user_by_id(user_id):
    """Get user by ID"""
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    return user
# ================================================================================
#                        PASSWORD RESET
# ================================================================================

def create_password_reset_token(user_id, token, expires_at):
    """Store password reset token for user"""
    db = get_db()
    try:
        # Delete any existing reset tokens for this user
        db.execute("DELETE FROM password_reset_tokens WHERE user_id = ?", (user_id,))
        
        db.execute(
            """INSERT INTO password_reset_tokens (user_id, token, expires_at) 
               VALUES (?, ?, ?)""",
            (user_id, token, expires_at)
        )
        db.commit()
        db.close()
        return True
    except sqlite3.IntegrityError:
        db.close()
        return False

def verify_reset_token(token):
    """Verify reset token and return user_id if valid"""
    db = get_db()
    
    # Check if token exists and hasn't expired
    reset_token = db.execute(
        """SELECT user_id FROM password_reset_tokens 
           WHERE token = ? AND expires_at > datetime('now')""",
        (token,)
    ).fetchone()
    
    db.close()
    
    if not reset_token:
        return None
    
    return reset_token['user_id']

def reset_password(user_id, new_password_hash, token):
    """Reset password and delete the used token"""
    db = get_db()
    
    # Update password
    db.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (new_password_hash, user_id)
    )
    
    # Delete the reset token
    db.execute("DELETE FROM password_reset_tokens WHERE token = ?", (token,))
    
    db.commit()
    db.close()
    return True

def cleanup_expired_reset_tokens():
    """Remove expired password reset tokens"""
    db = get_db()
    cur = db.cursor()
    
    cur.execute(
        "DELETE FROM password_reset_tokens WHERE expires_at < datetime('now')"
    )
    
    deleted_count = cur.rowcount
    db.commit()
    db.close()
    
    return deleted_count

# ================================================================================
#                        LOGIN HISTORY
# ================================================================================

def log_login(user_id, ip_address, user_agent, success=True):
    """Log a login attempt"""
    db = get_db()
    
    db.execute(
        """INSERT INTO login_history (user_id, ip_address, user_agent, success)
           VALUES (?, ?, ?, ?)""",
        (user_id, ip_address, user_agent, success)
    )
    
    db.commit()
    db.close()

def get_login_history(user_id, limit=10):
    """Get login history for a user"""
    db = get_db()
    
    logins = db.execute(
        """SELECT * FROM login_history 
           WHERE user_id = ? 
           ORDER BY login_time DESC 
           LIMIT ?""",
        (user_id, limit)
    ).fetchall()
    
    db.close()
    return logins

def cleanup_old_login_history(days_to_keep=90):
    """Remove login history older than specified days"""
    db = get_db()
    cur = db.cursor()
    
    cur.execute(
        """DELETE FROM login_history 
           WHERE login_time < datetime('now', '-' || ? || ' days')""",
        (days_to_keep,)
    )
    
    deleted_count = cur.rowcount
    db.commit()
    db.close()
    
    return deleted_count

# ================================================================================
#                        ADMIN MANAGEMENT
# ================================================================================

def set_user_role(user_id, role):
    """Set user role (admin or user)"""
    db = get_db()
    
    if role not in ['user', 'admin']:
        db.close()
        return False
    
    db.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
    db.commit()
    db.close()
    return True

def is_admin(user_id):
    """Check if user is admin"""
    user = get_user_by_id(user_id)
    return user and user['role'] == 'admin'

def get_all_users():
    """Get all users with their roles and creation dates"""
    db = get_db()
    
    users = db.execute(
        """SELECT id, username, email, role, created_at, email_verified FROM users ORDER BY created_at DESC"""
    ).fetchall()
    
    db.close()
    return users

def get_admin_stats():
    """Get admin dashboard statistics"""
    db = get_db()
    
    # Total users
    total_users = db.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
    
    # Verified users
    verified_users = db.execute("SELECT COUNT(*) as count FROM users WHERE email_verified = 1").fetchone()['count']
    
    # Total CO2 readings
    total_readings = db.execute("SELECT COUNT(*) as count FROM co2_readings").fetchone()['count']
    
    # Average PPM
    avg_ppm = db.execute("SELECT AVG(ppm) as avg FROM co2_readings").fetchone()['avg']
    
    # Recent logins (last 24 hours)
    recent_logins = db.execute(
        "SELECT COUNT(*) as count FROM login_history WHERE login_time > datetime('now', '-1 day')"
    ).fetchone()['count']
    
    # Admins count
    admin_count = db.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'").fetchone()['count']
    
    db.close()
    
    return {
        'total_users': total_users,
        'verified_users': verified_users,
        'total_readings': total_readings,
        'avg_ppm': round(avg_ppm, 1) if avg_ppm else 0,
        'recent_logins': recent_logins,
        'admin_count': admin_count
    }
def create_user(username, email, password_hash):
    """Create a new user"""
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        db.commit()
        user_id = cur.lastrowid
        db.close()
        return user_id
    except sqlite3.IntegrityError:
        db.close()
        return None

# ================================================================================
#                        USER SETTINGS MANAGEMENT
# ================================================================================

def get_user_settings(user_id):
    """Get user settings, create if doesn't exist"""
    db = get_db()
    settings = db.execute(
        "SELECT * FROM user_settings WHERE user_id = ?", 
        (user_id,)
    ).fetchone()
    
    if not settings:
        # Create default settings for new user
        db.execute(
            """INSERT INTO user_settings (user_id, good_threshold, bad_threshold, 
               alert_threshold, realistic_mode, update_speed, audio_alerts, email_alerts)
               VALUES (?, 800, 1200, 1400, 1, 1, 1, 1)""",
            (user_id,)
        )
        db.commit()
        settings = db.execute(
            "SELECT * FROM user_settings WHERE user_id = ?", 
            (user_id,)
        ).fetchone()
    
    db.close()
    return settings

def update_user_settings(user_id, **kwargs):
    """Update user settings"""
    db = get_db()
    allowed_fields = {
        'good_threshold', 'bad_threshold', 'alert_threshold', 
        'realistic_mode', 'update_speed', 'audio_alerts', 'email_alerts',
        'analysis_running'
    }
    
    fields_to_update = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not fields_to_update:
        db.close()
        return False
    
    set_clause = ", ".join([f"{k} = ?" for k in fields_to_update.keys()])
    values = list(fields_to_update.values()) + [user_id]
    
    db.execute(
        f"UPDATE user_settings SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
        values
    )
    db.commit()
    db.close()
    return True

def reset_user_settings(user_id):
    """Reset user settings to defaults"""
    return update_user_settings(
        user_id,
        good_threshold=800,
        bad_threshold=1200,
        alert_threshold=1400,
        realistic_mode=1,
        update_speed=1,
        audio_alerts=1,
        email_alerts=1
    )
# ================================================================================
#                        EMAIL VERIFICATION
# ================================================================================

def create_verification_token(user_id, token, expires_at):
    """Store verification token for user"""
    db = get_db()
    try:
        db.execute(
            """INSERT INTO verification_tokens (user_id, token, expires_at) 
               VALUES (?, ?, ?)""",
            (user_id, token, expires_at)
        )
        db.commit()
        db.close()
        return True
    except sqlite3.IntegrityError:
        db.close()
        return False

def verify_email_token(token):
    """Verify token and mark email as verified, returns user_id on success"""
    db = get_db()
    
    # Check if token exists and hasn't expired
    verification = db.execute(
        """SELECT user_id, expires_at FROM verification_tokens 
           WHERE token = ? AND expires_at > datetime('now')""",
        (token,)
    ).fetchone()
    
    if not verification:
        db.close()
        return None
    
    user_id = verification['user_id']
    
    # Mark user email as verified
    db.execute("UPDATE users SET email_verified = 1 WHERE id = ?", (user_id,))
    
    # Delete the token (it's been used)
    db.execute("DELETE FROM verification_tokens WHERE token = ?", (token,))
    
    db.commit()
    db.close()
    return user_id

def cleanup_expired_tokens():
    """Remove expired verification tokens"""
    db = get_db()
    cur = db.cursor()
    
    cur.execute(
        "DELETE FROM verification_tokens WHERE expires_at < datetime('now')"
    )
    
    deleted_count = cur.rowcount
    db.commit()
    db.close()
    
    return deleted_count

def get_user_by_email(email):
    """Get user by email"""
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    db.close()
    return user