"""
Admin routes
"""
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for, session
from .auth import login_required, admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_required
def index():
    """Admin dashboard"""
    from flask import current_app
    db = current_app.db
    
    # Get system statistics
    all_users = db.get_all_users()
    all_sensors = db.get_all_sensors()
    active_alerts = db.get_active_alerts()
    recent_logs = db.get_logs(limit=50)
    
    stats = {
        'total_users': len(all_users),
        'total_sensors': len(all_sensors),
        'active_alerts': len(active_alerts),
        'active_users': len([u for u in all_users if u['is_active']])
    }
    
    return render_template('admin/index.html',
                         stats=stats,
                         users=all_users,
                         sensors=all_sensors,
                         alerts=active_alerts,
                         logs=recent_logs)

@admin_bp.route('/users')
@admin_required
def users():
    """User management page"""
    from flask import current_app
    db = current_app.db
    
    all_users = db.get_all_users()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/logs')
@admin_required
def logs():
    """System logs page"""
    from flask import current_app
    db = current_app.db
    
    limit = request.args.get('limit', 100, type=int)
    logs = db.get_logs(limit=limit)
    
    return render_template('admin/logs.html', logs=logs)

@admin_bp.route('/api/system/stats')
@admin_required
def system_stats():
    """API endpoint for system statistics"""
    from flask import current_app
    db = current_app.db
    
    all_users = db.get_all_users()
    all_sensors = db.get_all_sensors()
    active_alerts = db.get_active_alerts()
    
    stats = {
        'total_users': len(all_users),
        'active_users': len([u for u in all_users if u['is_active']]),
        'total_sensors': len(all_sensors),
        'active_sensors': len([s for s in all_sensors if s['is_active']]),
        'active_alerts': len(active_alerts),
        'critical_alerts': len([a for a in active_alerts if a['alert_type'] == 'critical'])
    }
    
    return jsonify({'success': True, 'stats': stats})

@admin_bp.route('/api/user/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    """Toggle user active status"""
    from flask import current_app
    db = current_app.db
    
    # Prevent admin from deactivating themselves
    if user_id == session['user_id']:
        return jsonify({'success': False, 'error': 'Cannot deactivate your own account'}), 400
    
    user = db.get_user(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    new_status = 0 if user['is_active'] else 1
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_active = ? WHERE id = ?', (new_status, user_id))
    
    action = 'activated' if new_status else 'deactivated'
    db.log_action(f'user_{action}', session['user_id'], f"User {user['username']} {action}", request.remote_addr)
    
    return jsonify({'success': True, 'is_active': new_status})
