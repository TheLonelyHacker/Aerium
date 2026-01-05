# 🔌 API REFERENCE - ALL AVAILABLE ENDPOINTS

## Overview
All endpoints are served by Flask and require a logged-in user (except where noted). All responses use JSON format.

---

## 📊 Analytics Endpoints

### Get CO2 Predictions
```
GET /api/analytics/predict/<hours>
```
**Parameters:**
- `hours` (1-24) - Number of hours to predict

**Response:**
```json
{
  "success": true,
  "predictions": [850, 920, 980, ...]
}
```

### Get Predictions (Alternative Format)
```
GET /api/analytics/predictions?hours=N
```
**Query Parameters:**
- `hours` (default: 2) - Hours to predict

**Response:**
```json
{
  "success": true,
  "period_hours": 2,
  "predictions": [
    {"hour": 0, "predicted_co2": 850, "confidence": 85},
    {"hour": 2, "predicted_co2": 920, "confidence": 82}
  ]
}
```

### Detect Anomalies
```
GET /api/analytics/anomalies
```
**Query Parameters:**
- `days` (default: 7) - Days of history to analyze

**Response:**
```json
{
  "success": true,
  "anomalies": [
    {
      "id": 1,
      "timestamp": "2026-01-06T00:32:58Z",
      "type": "sudden_spike",
      "description": "Augmentation soudaine du CO₂ détectée",
      "value": 1450,
      "severity": "high"
    }
  ]
}
```

### Get Insights
```
GET /api/analytics/insights
```
**Query Parameters:**
- `days` (default: 30) - Days to analyze

**Response:**
```json
{
  "success": true,
  "insights": [
    {
      "id": 1,
      "title": "Pic d'activité détecté",
      "description": "Vous avez généralement des niveaux...",
      "recommendation": "Augmentez la ventilation...",
      "impact": "high"
    }
  ]
}
```

---

## 💚 Health Endpoints

### Get Health Recommendations
```
GET /api/health/recommendations
```

**Response:**
```json
{
  "success": true,
  "recommendations": [
    {
      "id": 1,
      "title": "Aérer votre espace",
      "description": "Ouvrez les fenêtres pendant 10-15 minutes",
      "priority": "high",
      "action_items": ["Open windows", "Use fans"],
      "expected_improvement": "15-20% reduction"
    }
  ]
}
```

---

## ⚡ System/Performance Endpoints

### Get Performance Metrics
```
GET /api/system/performance
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "database": {
      "total_queries": 15234,
      "avg_query_time": 12.5,
      "cache_hit_ratio": 0.87,
      "size_mb": 456.78
    },
    "optimization_tips": {
      "readings": "Add index on timestamp...",
      "analytics": "Consider partitioning..."
    }
  }
}
```

### Clear Cache
```
POST /api/system/cache/clear
```

**Response:**
```json
{
  "success": true,
  "message": "Cache cleared",
  "items_cleared": 1234,
  "freed_memory_mb": 123.45
}
```

### Archive Old Data
```
POST /api/system/archive
```

**Request Body:**
```json
{
  "days": 365
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "job_id": "archive_1234567890",
    "status": "queued",
    "days_archived": 365,
    "estimated_records": 5234,
    "estimated_time_seconds": 45
  }
}
```

---

## 👥 Collaboration Endpoints

### Get/Create Teams
```
GET /api/teams
POST /api/teams
```

**POST Request Body:**
```json
{
  "team_name": "Development Team",
  "description": "Our dev team"
}
```

**GET Response:**
```json
{
  "success": true,
  "teams": [
    {
      "id": 1,
      "name": "Équipe par Défaut",
      "description": "Votre équipe de travail",
      "owner": "Vous",
      "member_count": 1,
      "created_at": "2026-01-06T00:32:58Z"
    }
  ]
}
```

### Get/Add Team Members
```
GET /api/teams/<team_id>/members
POST /api/teams/<team_id>/members
```

**POST Request Body:**
```json
{
  "user_email": "john@example.com",
  "role": "member"
}
```

**GET Response:**
```json
{
  "success": true,
  "members": [
    {
      "email": "you@example.com",
      "role": "admin",
      "joined": "2026-01-06T00:32:58Z"
    }
  ]
}
```

### Get/Create Organizations
```
GET /api/organizations
POST /api/organizations
```

**POST Request Body:**
```json
{
  "name": "My Company",
  "tier": "free"
}
```

**GET Response:**
```json
{
  "success": true,
  "organizations": [
    {
      "id": 1,
      "name": "Mon Organisation",
      "tier": "free",
      "members": 5
    }
  ]
}
```

### Organization Members
```
GET /api/organizations/<org_id>/members
POST /api/organizations/<org_id>/members
```

### Organization Locations
```
GET /api/organizations/<org_id>/locations
POST /api/organizations/<org_id>/locations
```

### Organization Quotas
```
GET /api/organizations/<org_id>/quotas
```

**Response:**
```json
{
  "success": true,
  "quotas": {
    "sensors": {"used": 9, "limit": 20},
    "users": {"used": 6, "limit": 10},
    "storage": {"used": 3.5, "limit": 10},
    "readings": {"used": 7500, "limit": 10000}
  }
}
```

### Share Dashboard
```
POST /api/share/dashboard
```

**Request Body:**
```json
{
  "dashboard_name": "Team Dashboard"
}
```

**Response:**
```json
{
  "success": true,
  "share_link": "/shared/token123",
  "share_token": "token123"
}
```

### Get Shared Dashboards
```
GET /api/share/dashboards
```

### Generate Share Link
```
POST /api/share/link
```

---

## 📊 Visualization Endpoints

### Get Heatmap Data
```
GET /api/visualization/heatmap
```

**Query Parameters:**
- `days` (default: 30) - Days to analyze

**Response:**
```json
{
  "success": true,
  "heatmap": {
    "0": {"0": 850, "1": 820, "2": 880, ...},
    "1": {"0": 920, "1": 845, "2": 900, ...},
    ...
    "23": {"0": 750, "1": 780, "2": 820, ...}
  }
}
```

Format: `heatmap[hour][day] = co2_level`
- Hours: 0-23
- Days: 0-6 (Mon-Sun)

### Get Correlation Data
```
GET /api/visualization/correlation
```

**Query Parameters:**
- `variables` (comma-separated) - Variables to correlate

**Response:**
```json
{
  "success": true,
  "correlations": [
    {"name": "Température", "value": 0.68},
    {"name": "Humidité", "value": -0.42},
    {"name": "Activité", "value": 0.85},
    {"name": "Lumière", "value": 0.55}
  ]
}
```

### Dashboard Configuration
```
GET /api/dashboard/config
POST /api/dashboard/config
```

**GET Response:**
```json
{
  "success": true,
  "config": {
    "widgets": [
      {"id": "current_co2", "title": "Current CO₂", "enabled": true}
    ],
    "theme": "auto",
    "refresh_interval": 30
  }
}
```

### Export Visualization
```
POST /api/visualization/export
```

**Request Body:**
```json
{
  "format": "png",
  "viz_type": "heatmap"
}
```

---

## 📤 Export Endpoints

### Simulate Export
```
POST /api/export/simulate
```

**Request Body:**
```json
{
  "format": "csv",
  "period_days": 7,
  "sensor_id": "default"
}
```

**CSV Response:**
```
timestamp,co2_ppm
2026-01-06T00:32:58Z,850
2026-01-06T01:32:58Z,920
...
```

**JSON Response:**
```json
{
  "success": true,
  "format": "json",
  "export_date": "2026-01-06T00:32:58Z",
  "period_days": 7,
  "records": 168,
  "data": [
    {
      "timestamp": "2026-01-06T00:32:58Z",
      "co2": 850
    }
  ]
}
```

---

## 🔐 Authentication

### Login
```
POST /login
```

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin"
}
```

### Logout
```
GET /logout
```

---

## 📋 Additional Endpoints

### Get/Post Comments
```
GET /api/readings/<reading_id>/comments
POST /api/readings/<reading_id>/comments
```

### Create Alert
```
POST /api/alerts
```

### Get Activity
```
GET /api/activity
```

---

## 🔄 Response Format

All successful responses follow this format:
```json
{
  "success": true,
  "data": {...}
}
```

All error responses:
```json
{
  "success": false,
  "error": "Description of error"
}
```

---

## 📊 HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized (login required) |
| 403 | Forbidden (admin only) |
| 404 | Not Found |
| 500 | Server Error |

---

## 🔑 Key Endpoints Summary

| Purpose | Endpoint | Method |
|---------|----------|--------|
| Predictions | `/api/analytics/predictions?hours=N` | GET |
| Anomalies | `/api/analytics/anomalies` | GET |
| Insights | `/api/analytics/insights` | GET |
| Health | `/api/health/recommendations` | GET |
| Performance | `/api/system/performance` | GET |
| Cache Clear | `/api/system/cache/clear` | POST |
| Archive | `/api/system/archive` | POST |
| Teams | `/api/teams` | GET/POST |
| Organizations | `/api/organizations` | GET/POST |
| Share | `/api/share/dashboard` | POST |
| Heatmap | `/api/visualization/heatmap` | GET |
| Correlation | `/api/visualization/correlation` | GET |
| Export | `/api/export/simulate` | POST |

---

## 📝 Notes

- All endpoints require authentication (logged-in user)
- Some endpoints (admin) require admin role
- All timestamps are in ISO 8601 format (UTC)
- All data is simulated for demonstration purposes
- French language support throughout
- WebSocket connection available for real-time updates

---

**Last Updated**: 2026-01-06  
**API Version**: 1.0  
**Status**: ✅ All Endpoints Functional
