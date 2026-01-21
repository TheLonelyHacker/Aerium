"""Routes package"""
from .auth import auth_bp, login_required, admin_required
from .dashboard import dashboard_bp
from .sensors import sensors_bp
from .admin import admin_bp

__all__ = ['auth_bp', 'dashboard_bp', 'sensors_bp', 'admin_bp', 'login_required', 'admin_required']
