# 🚀 Advanced Features Implementation Guide

**Document Version:** 2.0  
**Date:** January 3, 2026  
**Status:** Ready for Integration  

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Module Structure](#module-structure)
3. [Installation & Integration](#installation--integration)
4. [API Endpoints](#api-endpoints)
5. [Feature Details](#feature-details)
6. [Database Schema](#database-schema)
7. [Frontend Implementation](#frontend-implementation)
8. [Testing](#testing)
9. [Performance Considerations](#performance-considerations)

---

## Overview

This document describes the advanced features module that adds four major capabilities to Morpheus:

### 🔍 **1. Analytics & Insights (AdvancedAnalytics)**
- **Predictive AI** - Predict CO₂ levels 1-24 hours ahead using linear regression
- **Anomaly Detection** - Find unusual readings using statistical analysis
- **Smart Insights** - Auto-generated insights about air quality patterns
- **Health Recommendations** - Personalized recommendations based on health research

### 👥 **2. Collaboration & Sharing (CollaborationManager)**
- **Shared Dashboards** - Create public/private dashboard links
- **Team Workspaces** - Manage team members and permissions
- **Share Links** - Generate shareable links with expiration
- **Permission Levels** - Admin, Editor, Viewer roles

### ⚡ **3. Performance & Optimization (PerformanceOptimizer)**
- **Smart Caching** - Cache predictions, insights, and aggregates
- **Database Optimization** - Query optimization and indexing recommendations
- **Data Archiving** - Archive old data to separate storage
- **Usage Analytics** - Track database usage and storage

### 📊 **4. Data Visualization (VisualizationEngine)**
- **Heatmaps** - Time-of-day patterns across week
- **Correlation Analysis** - Correlations between variables
- **Dashboard Customization** - Drag-and-drop widget system
- **Export Formats** - JSON, CSV, SVG export options

---

## Module Structure

### File 1: `advanced_features.py`
Contains four main classes:

```
advanced_features.py
├── AdvancedAnalytics
│   ├── predict_co2_level()        # Linear regression predictions
│   ├── detect_anomalies()         # Z-score based detection
│   ├── generate_insights()        # Rule-based insights
│   └── health_recommendation()    # Health recommendations
├── CollaborationManager
│   ├── create_shared_dashboard()  # Create shareable dashboard
│   ├── generate_share_link()      # Generate time-limited links
│   ├── validate_share_link()      # Validate tokens
│   └── create_team_workspace()    # Team collaboration
├── PerformanceOptimizer
│   ├── analyze_database_usage()   # Usage analytics
│   ├── optimize_queries()         # Query optimization tips
│   ├── archive_old_data()         # Data archiving
│   └── enable_smart_caching()     # Caching strategies
└── VisualizationEngine
    ├── generate_heatmap_data()      # Weekly heatmap
    ├── generate_correlation_data()  # Variable correlations
    ├── generate_dashboard_config()  # Dashboard layout
    └── export_visualization()       # Export functionality
```

### File 2: `advanced_features_routes.py`
Contains 25+ API endpoint definitions (scaffold):

```
advanced_features_routes.py
├── setup_analytics_routes()
│   ├── /api/analytics/predict/<hours>
│   ├── /api/analytics/anomalies
│   ├── /api/analytics/insights
│   └── /api/health/recommendations
├── setup_sharing_routes()
│   ├── /api/share/dashboard
│   ├── /api/share/link
│   ├── /api/teams
│   └── /api/teams/<id>/members
├── setup_visualization_routes()
│   ├── /api/visualization/heatmap
│   ├── /api/visualization/correlation
│   ├── /api/dashboard/config
│   └── /api/visualization/export
└── setup_optimization_routes()
    ├── /api/system/performance
    ├── /api/system/cache/clear
    └── /api/system/archive
```

---

## Installation & Integration

### Step 1: Add Files to Project
```bash
cp advanced_features.py ./site/
cp advanced_features_routes.py ./site/
```

### Step 2: Install Dependencies
```bash
pip install scikit-learn numpy
```

Add to `requirements.txt`:
```
scikit-learn>=1.0.0
numpy>=1.20.0
```

### Step 3: Integrate into app.py

**Add imports at top:**
```python
from advanced_features import (
    AdvancedAnalytics, 
    CollaborationManager,
    PerformanceOptimizer, 
    VisualizationEngine
)
from advanced_features_routes import register_advanced_features
```

**Register routes after app initialization:**
```python
# At the bottom of app.py, before socketio.run()
register_advanced_features(app, limiter)
```

### Step 4: Update Database Schema

Add these tables:

```sql
-- Shared dashboards
CREATE TABLE shared_dashboards (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    share_token TEXT UNIQUE NOT NULL,
    dashboard_name TEXT,
    is_public BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Teams
CREATE TABLE teams (
    id INTEGER PRIMARY KEY,
    workspace_id TEXT UNIQUE NOT NULL,
    creator_id INTEGER NOT NULL,
    team_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id)
);

-- Team members
CREATE TABLE team_members (
    id INTEGER PRIMARY KEY,
    team_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT DEFAULT 'viewer',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(team_id, user_id)
);

-- Cached analytics
CREATE TABLE cached_analytics (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    analytics_type TEXT,
    data JSON,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## API Endpoints

### Analytics & Insights

#### GET `/api/analytics/predict/<hours>`
Predict CO₂ levels for next N hours.

**Parameters:** hours (1-24)

**Response:**
```json
{
  "predicted_ppm": 850,
  "confidence": 87.5,
  "trend": "rising",
  "hours_ahead": 2
}
```

#### GET `/api/analytics/anomalies`
Detect anomalous readings.

**Parameters:** days (default: 7)

**Response:**
```json
{
  "anomalies": [
    {
      "index": 5,
      "ppm": 2100,
      "z_score": 3.2,
      "severity": "high",
      "timestamp": "2026-01-03T10:30:00Z"
    }
  ],
  "anomaly_count": 1,
  "statistics": {
    "mean": 850,
    "stdev": 120
  }
}
```

#### GET `/api/analytics/insights`
Get AI-generated insights.

**Parameters:** days (default: 30)

**Response:**
```json
{
  "insights": [
    {
      "type": "peak_time",
      "message": "CO₂ levels peak around 14:00",
      "confidence": 0.85,
      "action": "Consider ventilating around this time"
    },
    {
      "type": "air_quality",
      "message": "Air quality is moderate",
      "confidence": 0.85,
      "action": "Regular ventilation recommended"
    }
  ],
  "count": 2
}
```

#### GET `/api/health/recommendations`
Get health recommendations.

**Response:**
```json
{
  "recommendations": [
    {
      "level": "moderate",
      "symptom": "Possible minor concentration issues",
      "action": "Increase air circulation",
      "duration_minutes": 5
    }
  ],
  "current_ppm": 1050,
  "average_ppm": 900,
  "peak_ppm": 1400
}
```

### Visualization

#### GET `/api/visualization/heatmap`
Get heatmap data for time-of-day patterns.

**Parameters:** days (default: 30)

**Response:**
```json
{
  "heatmap": [[600, 620, ...], ...],
  "days": ["Mon", "Tue", ...],
  "hours": [0, 1, 2, ...],
  "min_value": 500,
  "max_value": 1500,
  "data_points": 5040
}
```

#### GET `/api/visualization/correlation`
Get correlation between variables.

**Parameters:** variables (comma-separated, default: ppm)

**Response:**
```json
{
  "correlations": [
    {
      "var1": "ppm",
      "var2": "temperature",
      "correlation": 0.65,
      "strength": "strong"
    }
  ],
  "variables": ["ppm"],
  "data_points": 5040
}
```

#### GET `/api/dashboard/config`
Get dashboard configuration.

**Response:**
```json
{
  "layout": "grid",
  "widgets": [
    {
      "id": "current-ppm",
      "name": "Current CO₂ Level",
      "type": "gauge",
      "position": 0,
      "size": "large",
      "enabled": true
    }
  ],
  "refresh_interval": 5,
  "theme": "auto"
}
```

### Collaboration & Sharing

#### POST `/api/share/dashboard`
Create a shared dashboard.

**Body:**
```json
{
  "name": "Living Room Monitor",
  "is_public": false
}
```

**Response:**
```json
{
  "share_token": "abc123...",
  "dashboard_name": "Living Room Monitor",
  "share_url": "/dashboard/shared/abc123...",
  "permissions": {
    "can_view": true,
    "can_edit": false,
    "can_export": true
  }
}
```

#### POST `/api/teams`
Create a team workspace.

**Body:**
```json
{
  "team_name": "My Team",
  "members": ["user@example.com"]
}
```

**Response:**
```json
{
  "workspace_id": "team123",
  "team_name": "My Team",
  "members": ["user@example.com"],
  "role_structure": {...}
}
```

---

## Feature Details

### Advanced Analytics

**Prediction Algorithm:**
- Linear Regression (sklearn)
- Uses last 10 readings as training data
- Confidence score = R² × 100
- Trend detection (rising/falling/stable)

**Anomaly Detection:**
- Z-score method (threshold: 2.0σ)
- Severity: medium (2-3σ), high (>3σ)
- Returns timestamp, PPM, z-score

**Insights Generation:**
- Peak time detection (hourly analysis)
- Air quality assessment (EPA standards)
- Trend analysis (7-day comparison)
- Pattern detection

**Health Recommendations:**
- EPA/WHO CO₂ guidelines
- Symptom descriptions
- Ventilation duration
- Action items

### Collaboration Features

**Share Links:**
- 32-character URL-safe tokens
- 30-day expiration default
- Access tracking
- Permission granularity

**Team Workspaces:**
- Admin/Editor/Viewer roles
- Email invitations
- Member management
- Shared analytics

### Performance Optimization

**Caching Strategy:**
- Predictions: 30-minute TTL
- Analytics: 1-hour TTL
- Insights: 6-hour TTL
- Dashboard: 5-minute TTL

**Database Optimization:**
- Indexes on timestamp, user_id
- Query result caching
- Data archiving (365+ days)
- Materialized views for aggregates

### Visualization

**Heatmap:**
- 7×24 matrix (days × hours)
- Average PPM per hour
- Color-coded intensity

**Correlation:**
- Pearson correlation coefficient
- Support multiple variables
- Strength classification

**Dashboard:**
- 5+ customizable widgets
- Drag-and-drop positioning
- User preferences storage
- Real-time auto-refresh

---

## Database Schema

### shared_dashboards Table
```
id              INTEGER PRIMARY KEY
user_id         INTEGER (FK: users)
share_token     TEXT UNIQUE
dashboard_name  TEXT
is_public       BOOLEAN
created_at      TIMESTAMP
expires_at      TIMESTAMP
access_count    INTEGER
```

### teams Table
```
id              INTEGER PRIMARY KEY
workspace_id    TEXT UNIQUE
creator_id      INTEGER (FK: users)
team_name       TEXT
created_at      TIMESTAMP
```

### team_members Table
```
id              INTEGER PRIMARY KEY
team_id         INTEGER (FK: teams)
user_id         INTEGER (FK: users)
role            TEXT (admin|editor|viewer)
joined_at       TIMESTAMP
```

### cached_analytics Table
```
id              INTEGER PRIMARY KEY
user_id         INTEGER (FK: users)
analytics_type  TEXT
data            JSON
cached_at       TIMESTAMP
expires_at      TIMESTAMP
```

---

## Frontend Implementation

### JavaScript Integration

```html
<!-- In base.html -->
<script src="{{ url_for('static', filename='js/advanced-features.js') }}"></script>

<!-- In dashboard.html -->
<div id="analytics-section">
  <div id="prediction-widget"></div>
  <div id="insights-widget"></div>
  <div id="heatmap-widget"></div>
</div>
```

### Advanced Features JS

```javascript
// Fetch predictions
async function getPredictions(hours = 2) {
  const res = await fetch(`/api/analytics/predict/${hours}`);
  return await res.json();
}

// Fetch insights
async function getInsights() {
  const res = await fetch('/api/analytics/insights');
  return await res.json();
}

// Fetch heatmap
async function getHeatmap() {
  const res = await fetch('/api/visualization/heatmap');
  return await res.json();
}

// Create shared dashboard
async function createSharedDashboard(name, isPublic) {
  const res = await fetch('/api/share/dashboard', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      name: name,
      is_public: isPublic
    })
  });
  return await res.json();
}
```

---

## Testing

### Unit Tests Example

```python
import pytest
from advanced_features import AdvancedAnalytics, VisualizationEngine

def test_predict_co2():
    readings = [
        {'ppm': 500, 'timestamp': '2026-01-01T10:00:00Z'},
        {'ppm': 550, 'timestamp': '2026-01-01T11:00:00Z'},
        {'ppm': 600, 'timestamp': '2026-01-01T12:00:00Z'},
    ]
    
    result = AdvancedAnalytics.predict_co2_level(readings, hours=1)
    
    assert 'predicted_ppm' in result
    assert 'confidence' in result
    assert result['confidence'] > 0

def test_detect_anomalies():
    readings = [
        {'ppm': 500}, {'ppm': 520}, {'ppm': 530},
        {'ppm': 2000},  # Anomaly
        {'ppm': 540}
    ]
    
    result = AdvancedAnalytics.detect_anomalies(readings)
    
    assert len(result['anomalies']) > 0
    assert result['anomalies'][0]['severity'] == 'high'

def test_heatmap():
    readings = [
        {'ppm': 600, 'timestamp': '2026-01-01T10:00:00Z'},
        {'ppm': 700, 'timestamp': '2026-01-08T10:00:00Z'},
    ]
    
    result = VisualizationEngine.generate_heatmap_data(readings)
    
    assert 'heatmap' in result
    assert len(result['heatmap']) == 7
```

---

## Performance Considerations

### Optimization Tips

1. **Predictions:** Cache results for 30 minutes
2. **Anomalies:** Run async detection job daily
3. **Insights:** Cache for 6 hours per user
4. **Heatmaps:** Pre-calculate hourly aggregates
5. **Queries:** Add indexes on timestamp, user_id

### Load Targets

- Predictions: <500ms response time
- Anomalies: <1s response time
- Insights: <2s response time
- Heatmap: <1.5s response time

### Caching Strategy

```
Predictions     → 30 min cache
Analytics       → 1 hour cache
Insights        → 6 hour cache
Dashboard       → 5 min cache
User prefs      → 24 hour cache
```

---

## Integration Checklist

- [ ] Copy `advanced_features.py` to site/
- [ ] Copy `advanced_features_routes.py` to site/
- [ ] Add imports to app.py
- [ ] Register routes in app.py
- [ ] Run `pip install scikit-learn numpy`
- [ ] Create database tables
- [ ] Create frontend widgets
- [ ] Test all endpoints
- [ ] Add documentation
- [ ] Deploy to production

---

## Troubleshooting

### ImportError: No module named 'sklearn'
```bash
pip install scikit-learn
```

### Predictions returning NaN
Check that you have at least 5 readings in the data.

### Slow heatmap queries
Add index: `CREATE INDEX idx_timestamp ON readings(timestamp);`

### Share links not working
Verify `share_token` is in database and not expired.

---

## Next Steps

1. ✅ **This Week:** Integrate all 4 feature modules
2. ✅ **Next Week:** Create frontend widgets for analytics
3. ✅ **Week 3:** Test and optimize query performance
4. ✅ **Week 4:** Deploy to production with monitoring

---

**Questions?** Check the main README.md or contact the development team.
