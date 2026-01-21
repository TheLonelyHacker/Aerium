"""
Sensor management routes
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from .auth import login_required
import random

sensors_bp = Blueprint('sensors', __name__, url_prefix='/sensors')

@sensors_bp.route('/')
@login_required
def index():
    """Sensor management page"""
    from flask import current_app
    db = current_app.db
    
    sensors = db.get_user_sensors(session['user_id'])
    return render_template('sensors/index.html', sensors=sensors)

@sensors_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new sensor"""
    if request.method == 'POST':
        from flask import current_app
        db = current_app.db
        
        name = request.form.get('name', '').strip()
        location = request.form.get('location', '').strip()
        threshold_good = request.form.get('threshold_good', 800, type=int)
        threshold_moderate = request.form.get('threshold_moderate', 1000, type=int)
        threshold_poor = request.form.get('threshold_poor', 1500, type=int)
        
        if not name or not location:
            flash('Name and location are required.', 'warning')
            return render_template('sensors/create.html')
        
        sensor_id = db.create_sensor(
            name=name,
            location=location,
            user_id=session['user_id'],
            threshold_good=threshold_good,
            threshold_moderate=threshold_moderate,
            threshold_poor=threshold_poor
        )
        
        db.log_action('sensor_created', session['user_id'], f"Created sensor: {name}", request.remote_addr)
        flash(f'Sensor "{name}" created successfully!', 'success')
        return redirect(url_for('sensors.index'))
    
    return render_template('sensors/create.html')

@sensors_bp.route('/<int:sensor_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(sensor_id):
    """Edit a sensor"""
    from flask import current_app
    db = current_app.db
    
    sensor = db.get_sensor(sensor_id)
    
    if not sensor or sensor['user_id'] != session['user_id']:
        flash('Sensor not found or access denied.', 'danger')
        return redirect(url_for('sensors.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        location = request.form.get('location', '').strip()
        threshold_good = request.form.get('threshold_good', type=int)
        threshold_moderate = request.form.get('threshold_moderate', type=int)
        threshold_poor = request.form.get('threshold_poor', type=int)
        
        if not name or not location:
            flash('Name and location are required.', 'warning')
            return render_template('sensors/edit.html', sensor=sensor)
        
        db.update_sensor(
            sensor_id,
            name=name,
            location=location,
            threshold_good=threshold_good,
            threshold_moderate=threshold_moderate,
            threshold_poor=threshold_poor
        )
        
        db.log_action('sensor_updated', session['user_id'], f"Updated sensor: {name}", request.remote_addr)
        flash(f'Sensor "{name}" updated successfully!', 'success')
        return redirect(url_for('sensors.index'))
    
    return render_template('sensors/edit.html', sensor=sensor)

@sensors_bp.route('/<int:sensor_id>/delete', methods=['POST'])
@login_required
def delete(sensor_id):
    """Delete a sensor"""
    from flask import current_app
    db = current_app.db
    
    sensor = db.get_sensor(sensor_id)
    
    if not sensor or sensor['user_id'] != session['user_id']:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    if db.delete_sensor(sensor_id):
        db.log_action('sensor_deleted', session['user_id'], f"Deleted sensor: {sensor['name']}", request.remote_addr)
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Failed to delete sensor'}), 500

@sensors_bp.route('/<int:sensor_id>/simulate', methods=['POST'])
@login_required
def simulate_reading(sensor_id):
    """Simulate a sensor reading (for testing)"""
    from flask import current_app
    from flask_socketio import emit
    db = current_app.db
    
    sensor = db.get_sensor(sensor_id)
    
    if not sensor or sensor['user_id'] != session['user_id']:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    # Generate random reading
    co2_level = random.randint(400, 2000)
    temperature = round(random.uniform(18.0, 26.0), 1)
    humidity = round(random.uniform(30.0, 70.0), 1)
    
    # Add reading to database
    reading_id = db.add_reading(sensor_id, co2_level, temperature, humidity)
    
    # Check thresholds and create alert if needed
    if co2_level >= sensor['threshold_poor']:
        alert_type = 'critical'
        message = f"Critical CO₂ level detected: {co2_level} ppm"
        db.create_alert(sensor_id, alert_type, message, co2_level)
    elif co2_level >= sensor['threshold_moderate']:
        alert_type = 'warning'
        message = f"High CO₂ level detected: {co2_level} ppm"
        db.create_alert(sensor_id, alert_type, message, co2_level)
    
    # Get the full reading
    reading = db.get_latest_reading(sensor_id)
    
    # Emit via WebSocket
    try:
        socketio = current_app.extensions.get('socketio')
        if socketio:
            socketio.emit('new_reading', {
                'sensor_id': sensor_id,
                'reading': reading
            }, namespace='/')
    except:
        pass  # Socket.IO might not be initialized yet
    
    return jsonify({
        'success': True,
        'reading': reading
    })

@sensors_bp.route('/<int:sensor_id>/details')
@login_required
def details(sensor_id):
    """Sensor details page with charts"""
    from flask import current_app
    db = current_app.db
    
    sensor = db.get_sensor(sensor_id)
    
    if not sensor or sensor['user_id'] != session['user_id']:
        flash('Sensor not found or access denied.', 'danger')
        return redirect(url_for('sensors.index'))
    
    # Get recent readings
    readings = db.get_readings(sensor_id, hours=24, limit=100)
    
    # Get statistics
    stats_24h = db.get_statistics(sensor_id, hours=24)
    stats_7d = db.get_statistics(sensor_id, hours=168)
    
    # Get active alerts
    alerts = db.get_active_alerts(sensor_id)
    
    return render_template('sensors/details.html',
                         sensor=sensor,
                         readings=readings,
                         stats_24h=stats_24h,
                         stats_7d=stats_7d,
                         alerts=alerts)
