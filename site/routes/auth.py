"""
Authentication routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        from flask import current_app
        db = current_app.db
        
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter both username and password.', 'warning')
            return render_template('auth/login.html')
        
        user = db.verify_user(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session.permanent = True
            
            # Log the action
            db.log_action('user_login', user['id'], f"User {username} logged in", request.remote_addr)
            
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password.', 'danger')
            db.log_action('failed_login', None, f"Failed login attempt for {username}", request.remote_addr)
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        from flask import current_app
        db = current_app.db
        
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # Validation
        if not all([username, email, password, password_confirm]):
            flash('All fields are required.', 'warning')
            return render_template('auth/register.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'warning')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'warning')
            return render_template('auth/register.html')
        
        if password != password_confirm:
            flash('Passwords do not match.', 'warning')
            return render_template('auth/register.html')
        
        # Create user
        user_id = db.create_user(username, email, password)
        
        if user_id:
            db.log_action('user_register', user_id, f"New user {username} registered", request.remote_addr)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Username or email already exists.', 'danger')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    """Logout user"""
    from flask import current_app
    db = current_app.db
    
    if 'user_id' in session:
        db.log_action('user_logout', session['user_id'], f"User {session['username']} logged out", request.remote_addr)
    
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    from flask import current_app
    db = current_app.db
    
    user = db.get_user(session['user_id'])
    return render_template('auth/profile.html', user=user)
