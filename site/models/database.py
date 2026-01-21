"""
Database models and operations for Aerium
"""
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import os

class Database:
    """Database manager for Aerium application"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_data_directory()
        self._init_database()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            # Sensors table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location TEXT,
                    sensor_type TEXT DEFAULT 'CO2',
                    threshold_good INTEGER DEFAULT 800,
                    threshold_moderate INTEGER DEFAULT 1000,
                    threshold_poor INTEGER DEFAULT 1500,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Readings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_id INTEGER NOT NULL,
                    co2_level REAL NOT NULL,
                    temperature REAL,
                    humidity REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
                )
            ''')
            
            # Alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_id INTEGER NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    co2_level REAL NOT NULL,
                    is_resolved INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
                )
            ''')
            
            # System logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_readings_sensor ON readings(sensor_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON readings(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_sensor ON alerts(sensor_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_user ON system_logs(user_id)')
            
            conn.commit()
    
    # User methods
    def create_user(self, username: str, email: str, password: str, role: str = 'user') -> Optional[int]:
        """Create a new user"""
        salt = secrets.token_hex(32)
        password_hash = self._hash_password(password, salt)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, salt, role)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, email, password_hash, salt, role))
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify user credentials"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, password_hash, salt, role, is_active
                FROM users WHERE username = ?
            ''', (username,))
            user = cursor.fetchone()
            
            if user and user['is_active']:
                password_hash = self._hash_password(password, user['salt'])
                if password_hash == user['password_hash']:
                    # Update last login
                    cursor.execute('''
                        UPDATE users SET last_login = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (user['id'],))
                    return dict(user)
        return None
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (admin only)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, email, role, created_at, last_login, is_active FROM users')
            return [dict(row) for row in cursor.fetchall()]
    
    # Sensor methods
    def create_sensor(self, name: str, location: str, user_id: int, **kwargs) -> int:
        """Create a new sensor"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sensors (name, location, user_id, threshold_good, threshold_moderate, threshold_poor)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                name, location, user_id,
                kwargs.get('threshold_good', 800),
                kwargs.get('threshold_moderate', 1000),
                kwargs.get('threshold_poor', 1500)
            ))
            return cursor.lastrowid
    
    def get_sensor(self, sensor_id: int) -> Optional[Dict[str, Any]]:
        """Get sensor by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sensors WHERE id = ?', (sensor_id,))
            sensor = cursor.fetchone()
            return dict(sensor) if sensor else None
    
    def get_user_sensors(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all sensors for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sensors WHERE user_id = ? AND is_active = 1', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_sensors(self) -> List[Dict[str, Any]]:
        """Get all active sensors"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sensors WHERE is_active = 1')
            return [dict(row) for row in cursor.fetchall()]
    
    def update_sensor(self, sensor_id: int, **kwargs) -> bool:
        """Update sensor settings"""
        allowed_fields = ['name', 'location', 'threshold_good', 'threshold_moderate', 'threshold_poor', 'is_active']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [sensor_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE sensors SET {set_clause} WHERE id = ?', values)
            return cursor.rowcount > 0
    
    def delete_sensor(self, sensor_id: int) -> bool:
        """Soft delete a sensor"""
        return self.update_sensor(sensor_id, is_active=0)
    
    # Reading methods
    def add_reading(self, sensor_id: int, co2_level: float, temperature: float = None, humidity: float = None) -> int:
        """Add a new sensor reading"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO readings (sensor_id, co2_level, temperature, humidity)
                VALUES (?, ?, ?, ?)
            ''', (sensor_id, co2_level, temperature, humidity))
            return cursor.lastrowid
    
    def get_latest_reading(self, sensor_id: int) -> Optional[Dict[str, Any]]:
        """Get the latest reading for a sensor"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM readings WHERE sensor_id = ?
                ORDER BY timestamp DESC LIMIT 1
            ''', (sensor_id,))
            reading = cursor.fetchone()
            return dict(reading) if reading else None
    
    def get_readings(self, sensor_id: int, hours: int = 24, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get readings for a sensor within time range"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            since = datetime.now() - timedelta(hours=hours)
            cursor.execute('''
                SELECT * FROM readings
                WHERE sensor_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (sensor_id, since, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self, sensor_id: int, hours: int = 24) -> Dict[str, Any]:
        """Get statistics for a sensor"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            since = datetime.now() - timedelta(hours=hours)
            cursor.execute('''
                SELECT
                    COUNT(*) as count,
                    AVG(co2_level) as avg_co2,
                    MIN(co2_level) as min_co2,
                    MAX(co2_level) as max_co2,
                    AVG(temperature) as avg_temp,
                    AVG(humidity) as avg_humidity
                FROM readings
                WHERE sensor_id = ? AND timestamp >= ?
            ''', (sensor_id, since))
            result = cursor.fetchone()
            return dict(result) if result else {}
    
    # Alert methods
    def create_alert(self, sensor_id: int, alert_type: str, message: str, co2_level: float) -> int:
        """Create a new alert"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alerts (sensor_id, alert_type, message, co2_level)
                VALUES (?, ?, ?, ?)
            ''', (sensor_id, alert_type, message, co2_level))
            return cursor.lastrowid
    
    def get_active_alerts(self, sensor_id: int = None) -> List[Dict[str, Any]]:
        """Get active alerts"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if sensor_id:
                cursor.execute('''
                    SELECT a.*, s.name as sensor_name, s.location
                    FROM alerts a
                    JOIN sensors s ON a.sensor_id = s.id
                    WHERE a.sensor_id = ? AND a.is_resolved = 0
                    ORDER BY a.created_at DESC
                ''', (sensor_id,))
            else:
                cursor.execute('''
                    SELECT a.*, s.name as sensor_name, s.location
                    FROM alerts a
                    JOIN sensors s ON a.sensor_id = s.id
                    WHERE a.is_resolved = 0
                    ORDER BY a.created_at DESC
                ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def resolve_alert(self, alert_id: int) -> bool:
        """Mark alert as resolved"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE alerts SET is_resolved = 1, resolved_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (alert_id,))
            return cursor.rowcount > 0
    
    # System log methods
    def log_action(self, action: str, user_id: int = None, details: str = None, ip_address: str = None):
        """Log a system action"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO system_logs (user_id, action, details, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (user_id, action, details, ip_address))
    
    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent system logs"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT l.*, u.username
                FROM system_logs l
                LEFT JOIN users u ON l.user_id = u.id
                ORDER BY l.timestamp DESC
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # Utility methods
    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """Hash password with salt"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
