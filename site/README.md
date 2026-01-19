# Aerium v2.0 - Rebuilt from Scratch

## 🎉 What's New

This is a **complete rebuild** of the Aerium CO₂ monitoring webapp with modern architecture and best practices.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
cd site
python app.py
```

### 3. Access the Application

Open your browser and navigate to: **http://localhost:5000**

## 🔐 Demo Credentials

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`

### Regular User Account
- **Username**: `demo`
- **Password**: `demo123`

## ✨ Key Features

### 🔒 Authentication & Security
- Secure user registration and login
- Role-based access control (User/Admin)
- Password hashing with PBKDF2
- Session management
- Rate limiting for API endpoints

### 📊 Real-time Monitoring
- Live CO₂ level updates via WebSocket
- Multiple sensor support
- Custom threshold configuration per sensor
- Real-time alerts for threshold violations
- Interactive Chart.js visualizations

### 🎛️ Sensor Management
- Create, edit, and delete sensors
- Configure custom thresholds (Good/Moderate/Poor/Critical)
- Assign locations to sensors
- Simulate readings for testing
- View historical data and trends

### 📈 Data Analytics
- 24-hour statistics (Min/Max/Average)
- 7-day trend analysis
- Historical data tracking
- Export capabilities (future feature)

### 👨‍💼 Admin Dashboard
- User management (activate/deactivate users)
- System statistics overview
- Activity audit logs
- Sensor monitoring across all users

### 🎨 Modern UI/UX
- Responsive Bootstrap 5 design
- Mobile-friendly interface
- Intuitive navigation
- Custom styling and animations
- Error handling pages (404, 403, 500)

## 🏗️ Architecture

### Project Structure

```
site/
├── app.py                 # Main Flask application
├── config/                # Configuration management
│   ├── __init__.py
│   └── settings.py        # Environment-based configs
├── models/                # Database models
│   ├── __init__.py
│   └── database.py        # SQLite database layer
├── routes/                # Blueprint routes
│   ├── __init__.py
│   ├── auth.py           # Authentication routes
│   ├── dashboard.py      # Dashboard routes
│   ├── sensors.py        # Sensor management routes
│   └── admin.py          # Admin routes
├── templates/             # Jinja2 templates
│   ├── base.html         # Base template
│   ├── index.html        # Landing page
│   ├── auth/             # Auth templates
│   ├── dashboard/        # Dashboard templates
│   ├── sensors/          # Sensor templates
│   ├── admin/            # Admin templates
│   └── errors/           # Error pages
└── static/                # Static assets
    ├── css/
    │   └── style.css     # Custom styles
    └── js/
        └── main.js       # JavaScript utilities
```

### Technology Stack

- **Backend**: Flask 3.0+, Python 3.8+
- **Database**: SQLite with proper indexing
- **Real-time**: Flask-SocketIO, Socket.IO
- **Frontend**: Bootstrap 5, Chart.js, FontAwesome
- **Security**: Flask-Limiter, secure sessions

## 📋 Database Schema

### Tables
1. **users** - User accounts and authentication
2. **sensors** - CO₂ sensor configurations
3. **readings** - Sensor measurement data
4. **alerts** - Threshold violation alerts
5. **system_logs** - Activity audit trail

## 🔧 Configuration

Edit `site/config/settings.py` to customize:

- Secret key
- Database path
- Session settings
- CO₂ thresholds
- Rate limiting
- Cache settings

## 🧪 Testing

The application includes:
- Automatic demo data initialization
- Sensor reading simulation
- Test user accounts
- Sample sensor configuration

### Test a Sensor Reading

1. Log in with demo credentials
2. Go to "Dashboard"
3. Click "Simulate" on any sensor card
4. Watch the real-time update!

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

## 🔐 Security Features

- Password hashing with salt
- CSRF protection
- Session security
- Rate limiting
- SQL injection prevention
- XSS protection

## 📊 Monitoring Dashboard

### User Dashboard
- View all your sensors
- Real-time CO₂ levels
- 24h statistics
- Active alerts
- Quick access to sensor details

### Admin Dashboard
- System-wide statistics
- User management
- All sensors overview
- Activity logs
- User activation controls

## 🎯 Use Cases

- **🏢 Offices**: Monitor workspace air quality
- **🏫 Schools**: Ensure optimal learning environments
- **🏠 Homes**: Track indoor air quality
- **🏭 Industry**: Compliance monitoring
- **🔬 Research**: Environmental data collection

## 🛠️ Development

### Requirements
- Python 3.8 or higher
- pip (Python package manager)

### Installation for Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
cd site
python app.py
```

## 📝 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### Dashboard
- `GET /dashboard/` - Main dashboard
- `GET /dashboard/api/sensors` - Get user sensors
- `GET /dashboard/api/sensor/<id>/latest` - Latest reading

### Sensors
- `GET /sensors/` - List sensors
- `POST /sensors/create` - Create sensor
- `GET /sensors/<id>/details` - Sensor details
- `POST /sensors/<id>/simulate` - Simulate reading

### Admin (Admin only)
- `GET /admin/` - Admin dashboard
- `POST /admin/api/user/<id>/toggle` - Toggle user status

## 🐛 Troubleshooting

### Application won't start
- Check Python version (3.8+)
- Ensure all dependencies are installed
- Verify database directory is writable

### Database errors
- Delete `data/aerium.db` to reset
- Application will recreate on next start

### WebSocket not working
- Check firewall settings
- Ensure port 5000 is not blocked
- Try using a different browser

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Credits

- Flask framework
- Bootstrap 5
- Chart.js
- FontAwesome
- Socket.IO

## 📧 Support

For issues or questions, please open an issue on GitHub.

---

**Version**: 2.0  
**Last Updated**: January 2026  
**Status**: Production Ready ✅

Made with ❤️ for healthier air quality monitoring
