"""
Aerium - CO2 Air Quality Monitoring System
Main Flask Application
"""
from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

# Import configuration and models
from config import config
from models import Database

# Import routes
from routes import auth_bp, dashboard_bp, sensors_bp, admin_bp

def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize database
    app.db = Database(app.config['DATABASE_PATH'])
    
    # Initialize extensions
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode=app.config['SOCKETIO_ASYNC_MODE'])
    
    # Rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=app.config['RATELIMIT_STORAGE_URL'],
        default_limits=[app.config['RATELIMIT_DEFAULT']]
    )
    
    # Store extensions in app
    app.extensions['socketio'] = socketio
    app.extensions['limiter'] = limiter
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(sensors_bp)
    app.register_blueprint(admin_bp)
    
    # Root route
    @app.route('/')
    def index():
        """Landing page"""
        return render_template('index.html')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    # WebSocket events
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print(f'Client connected')
        emit('connection_response', {'status': 'connected'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print('Client disconnected')
    
    @socketio.on('subscribe_sensor')
    def handle_sensor_subscription(data):
        """Subscribe to sensor updates"""
        sensor_id = data.get('sensor_id')
        print(f'Client subscribed to sensor {sensor_id}')
        emit('subscription_confirmed', {'sensor_id': sensor_id})
    
    # Template filters
    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
        """Format datetime for templates"""
        if value is None:
            return ''
        from datetime import datetime
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except:
                return value
        return value.strftime(format)
    
    @app.template_filter('co2_status')
    def co2_status(value, thresholds=None):
        """Determine CO2 status"""
        if thresholds is None:
            thresholds = {
                'good': app.config['CO2_THRESHOLD_GOOD'],
                'moderate': app.config['CO2_THRESHOLD_MODERATE'],
                'poor': app.config['CO2_THRESHOLD_POOR']
            }
        
        if value < thresholds['good']:
            return 'good'
        elif value < thresholds['moderate']:
            return 'moderate'
        elif value < thresholds['poor']:
            return 'poor'
        else:
            return 'critical'
    
    @app.template_filter('co2_color')
    def co2_color(value, thresholds=None):
        """Get color for CO2 level"""
        status = co2_status(value, thresholds)
        colors = {
            'good': 'success',
            'moderate': 'warning',
            'poor': 'orange',
            'critical': 'danger'
        }
        return colors.get(status, 'secondary')
    
    return app, socketio

def init_demo_data(db):
    """Initialize demo data for testing"""
    # Create admin user
    admin_id = db.create_user('admin', 'admin@aerium.local', 'admin123', 'admin')
    if admin_id:
        print('✓ Demo admin user created (username: admin, password: admin123)')
        
        # Create a demo sensor
        sensor_id = db.create_sensor(
            name='Office Sensor',
            location='Main Office',
            user_id=admin_id,
            threshold_good=800,
            threshold_moderate=1000,
            threshold_poor=1500
        )
        print(f'✓ Demo sensor created (ID: {sensor_id})')
    
    # Create regular user
    user_id = db.create_user('demo', 'demo@aerium.local', 'demo123', 'user')
    if user_id:
        print('✓ Demo user created (username: demo, password: demo123)')

if __name__ == '__main__':
    # Create application
    app, socketio = create_app('development')
    
    # Initialize demo data if database is empty
    with app.db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM users')
        user_count = cursor.fetchone()['count']
        
        if user_count == 0:
            print('\n=== Initializing demo data ===')
            init_demo_data(app.db)
            print('=== Demo data initialized ===\n')
    
    print('=' * 60)
    print('🌬️  Aerium - CO2 Air Quality Monitoring System')
    print('=' * 60)
    print('🚀 Starting server...')
    print('📍 URL: http://localhost:5000')
    print('👤 Demo Login:')
    print('   - Admin: admin / admin123')
    print('   - User:  demo / demo123')
    print('=' * 60)
    
    # Run the app
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
