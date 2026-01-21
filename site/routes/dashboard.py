"""
Dashboard routes
"""
from flask import Blueprint, render_template, jsonify, request
from .auth import login_required

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard page"""
    from flask import current_app, session
    db = current_app.db
    
    # Get user's sensors
    sensors = db.get_user_sensors(session['user_id'])
    
    # Get latest readings and alerts for each sensor
    sensor_data = []
    for sensor in sensors:
        latest_reading = db.get_latest_reading(sensor['id'])
        stats = db.get_statistics(sensor['id'], hours=24)
        active_alerts = db.get_active_alerts(sensor['id'])
        
        sensor_data.append({
            'sensor': sensor,
            'latest_reading': latest_reading,
            'stats': stats,
            'alerts': active_alerts
        })
    
    return render_template('dashboard/index.html', sensor_data=sensor_data)

@dashboard_bp.route('/api/sensors')
@login_required
def get_sensors():
    """API endpoint to get user's sensors"""
    from flask import current_app, session
    db = current_app.db
    
    sensors = db.get_user_sensors(session['user_id'])
    return jsonify({'success': True, 'sensors': sensors})

@dashboard_bp.route('/api/sensor/<int:sensor_id>/latest')
@login_required
def get_latest_reading(sensor_id):
    """API endpoint to get latest reading for a sensor"""
    from flask import current_app
    db = current_app.db
    
    reading = db.get_latest_reading(sensor_id)
    if reading:
        return jsonify({'success': True, 'reading': reading})
    return jsonify({'success': False, 'error': 'No readings found'}), 404

@dashboard_bp.route('/api/sensor/<int:sensor_id>/readings')
@login_required
def get_readings(sensor_id):
    """API endpoint to get readings for a sensor"""
    from flask import current_app
    db = current_app.db
    
    hours = request.args.get('hours', 24, type=int)
    limit = request.args.get('limit', 1000, type=int)
    
    readings = db.get_readings(sensor_id, hours=hours, limit=limit)
    return jsonify({'success': True, 'readings': readings})

@dashboard_bp.route('/api/sensor/<int:sensor_id>/statistics')
@login_required
def get_statistics(sensor_id):
    """API endpoint to get statistics for a sensor"""
    from flask import current_app
    db = current_app.db
    
    hours = request.args.get('hours', 24, type=int)
    stats = db.get_statistics(sensor_id, hours=hours)
    
    return jsonify({'success': True, 'statistics': stats})

@dashboard_bp.route('/api/alerts')
@login_required
def get_alerts():
    """API endpoint to get active alerts"""
    from flask import current_app
    db = current_app.db
    
    alerts = db.get_active_alerts()
    return jsonify({'success': True, 'alerts': alerts})

@dashboard_bp.route('/api/alert/<int:alert_id>/resolve', methods=['POST'])
@login_required
def resolve_alert(alert_id):
    """API endpoint to resolve an alert"""
    from flask import current_app, session
    db = current_app.db
    
    if db.resolve_alert(alert_id):
        db.log_action('alert_resolved', session['user_id'], f"Alert {alert_id} resolved", request.remote_addr)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Alert not found'}), 404
