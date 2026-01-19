"""
Application Constants
Centralized configuration values used throughout the application
"""

# ==================== CO₂ THRESHOLDS ====================
# Default CO₂ level thresholds (in ppm)
CO2_THRESHOLD_GOOD = 800
CO2_THRESHOLD_WARNING = 1000
CO2_THRESHOLD_CRITICAL = 1200

# Custom threshold ranges
CO2_MIN_THRESHOLD = 400
CO2_MAX_THRESHOLD = 2000

# ==================== SESSION & AUTH ====================
EMAIL_VERIFICATION_EXPIRY_HOURS = 24
PASSWORD_RESET_EXPIRY_MINUTES = 60
SESSION_LIFETIME_DAYS = 7

# ==================== DATA CLEANUP ====================
# Cleanup policies (in days)
CLEANUP_AUDIT_LOGS_DAYS = 90
CLEANUP_LOGIN_HISTORY_DAYS = 180
CLEANUP_OLD_DATA_DAYS = 365

# ==================== CACHE SETTINGS ====================
CACHE_TIMEOUT_SECONDS = 600  # 10 minutes
CACHE_ANALYTICS_TIMEOUT = 1800  # 30 minutes
CACHE_DASHBOARD_TIMEOUT = 300  # 5 minutes

# ==================== PAGINATION ====================
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 500
MIN_PAGE_SIZE = 1

# ==================== FILE UPLOADS ====================
MAX_IMPORT_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMPORT_EXTENSIONS = ['csv', 'xlsx', 'xls']
MAX_IMPORT_ROWS = 10000

# ==================== EXPORT SETTINGS ====================
EXPORT_BATCH_SIZE = 1000  # Rows per batch
MAX_EXPORT_ROWS = 50000
EXPORT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# ==================== SENSOR SETTINGS ====================
MAX_SENSORS_PER_USER = 50
SENSOR_READ_TIMEOUT_SECONDS = 30
SENSOR_AVAILABILITY_CHECK_INTERVAL = 300  # 5 minutes

# ==================== DATABASE ====================
DATABASE_BACKUP_RETENTION_DAYS = 30
DB_QUERY_TIMEOUT = 30  # seconds

# ==================== ANALYTICS ====================
MIN_READINGS_FOR_PREDICTION = 5
ML_PREDICTION_HOURS_MAX = 24
ML_ANOMALY_THRESHOLD_STD = 2.0
ANOMALY_DETECTION_MIN_READINGS = 3

# ==================== COLLABORATION ====================
SHARED_DASHBOARD_EXPIRY_DAYS = 90
MAX_COLLABORATORS_PER_DASHBOARD = 100
COLLABORATION_MESSAGE_MAX_LENGTH = 500
MAX_TEAM_SIZE = 1000

# ==================== NOTIFICATIONS ====================
NOTIFICATION_RETENTION_DAYS = 30
MAX_NOTIFICATIONS_PER_USER = 1000

# ==================== SIMULATOR ====================
SIMULATOR_DEFAULT_SPEED = 1.0  # 1x speed
SIMULATOR_MIN_SPEED = 0.1
SIMULATOR_MAX_SPEED = 10.0

# ==================== TEMPERATURE & HUMIDITY ====================
TEMPERATURE_MIN = -10.0
TEMPERATURE_MAX = 50.0
HUMIDITY_MIN = 0.0
HUMIDITY_MAX = 100.0

# ==================== USER ROLES ====================
ROLE_ADMIN = 'admin'
ROLE_USER = 'user'
ROLE_GUEST = 'guest'
ROLE_TEAM_OWNER = 'owner'
ROLE_TEAM_MEMBER = 'member'

VALID_ROLES = [ROLE_ADMIN, ROLE_USER, ROLE_GUEST]
VALID_TEAM_ROLES = [ROLE_TEAM_OWNER, ROLE_TEAM_MEMBER]

# ==================== PERMISSIONS ====================
PERMISSION_READ = 'read'
PERMISSION_WRITE = 'write'
PERMISSION_DELETE = 'delete'
PERMISSION_ADMIN = 'admin'
PERMISSION_EXPORT = 'export'
PERMISSION_IMPORT = 'import'
PERMISSION_COLLABORATE = 'collaborate'

ADMIN_PERMISSIONS = [
    PERMISSION_READ,
    PERMISSION_WRITE,
    PERMISSION_DELETE,
    PERMISSION_ADMIN,
    PERMISSION_EXPORT,
    PERMISSION_IMPORT,
    PERMISSION_COLLABORATE
]

# ==================== AUDIT LOG ACTIONS ====================
ACTION_USER_LOGIN = 'user_login'
ACTION_USER_LOGOUT = 'user_logout'
ACTION_USER_CREATED = 'user_created'
ACTION_USER_DELETED = 'user_deleted'
ACTION_ROLE_CHANGED = 'role_changed'
ACTION_PASSWORD_CHANGED = 'password_changed'
ACTION_SENSOR_CREATED = 'sensor_created'
ACTION_SENSOR_DELETED = 'sensor_deleted'
ACTION_DATA_EXPORTED = 'data_exported'
ACTION_DATA_IMPORTED = 'data_imported'
ACTION_SETTINGS_CHANGED = 'settings_changed'

# ==================== NOTIFICATION TYPES ====================
NOTIFICATION_TYPE_INFO = 'info'
NOTIFICATION_TYPE_WARNING = 'warning'
NOTIFICATION_TYPE_ERROR = 'error'
NOTIFICATION_TYPE_SUCCESS = 'success'
NOTIFICATION_TYPE_ALERT = 'alert'

# ==================== API ENDPOINTS ====================
API_VERSION = 'v1'
API_PREFIX = f'/api/{API_VERSION}'

# ==================== WEBSOCKET EVENTS ====================
WEBSOCKET_EVENT_DATA_UPDATE = 'data_update'
WEBSOCKET_EVENT_ALERT = 'alert'
WEBSOCKET_EVENT_USER_JOINED = 'user_joined'
WEBSOCKET_EVENT_USER_LEFT = 'user_left'
WEBSOCKET_EVENT_DASHBOARD_SYNC = 'dashboard_sync'
WEBSOCKET_EVENT_COMMENT = 'comment'

# ==================== ERROR MESSAGES ====================
ERROR_INVALID_CREDENTIALS = "Invalid username or password"
ERROR_USER_NOT_FOUND = "User not found"
ERROR_EMAIL_ALREADY_EXISTS = "Email address already registered"
ERROR_USERNAME_ALREADY_EXISTS = "Username already taken"
ERROR_INVALID_TOKEN = "Invalid or expired token"
ERROR_UNAUTHORIZED = "You do not have permission to access this resource"
ERROR_SENSOR_NOT_FOUND = "Sensor not found"
ERROR_DATABASE_ERROR = "A database error occurred"
ERROR_INVALID_INPUT = "Invalid input provided"

# ==================== RESPONSE MESSAGES ====================
MSG_SUCCESS = "Operation completed successfully"
MSG_CREATED = "Resource created successfully"
MSG_UPDATED = "Resource updated successfully"
MSG_DELETED = "Resource deleted successfully"
MSG_EMAIL_SENT = "Email sent successfully"
MSG_EXPORT_STARTED = "Export process started"
MSG_IMPORT_COMPLETED = "Data import completed"
