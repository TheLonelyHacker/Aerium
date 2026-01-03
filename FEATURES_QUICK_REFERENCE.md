# Quick Reference: 6 New Features

## 🚀 Feature Overview

| Feature | Purpose | Status | Location |
|---------|---------|--------|----------|
| **Feature 4** | Custom Thresholds | ✅ Complete | Settings page |
| **Feature 5** | Historical Comparison | ✅ Complete | API: /api/analytics/* |
| **Feature 6** | Data Visualization | ✅ Complete | /visualization |
| **Feature 7** | User Roles & Permissions | ✅ Complete | API: /api/permissions/* |
| **Feature 9** | CSV Data Import | ✅ Complete | Admin > Maintenance |
| **Feature 10** | Rate Limiting & Security | ✅ Complete | Global (all endpoints) |

---

## 📊 Feature 4: Custom Thresholds

**Where:** Settings > Thresholds

**What it does:** Set your personal CO₂ alert levels
- Good PPM (green, safe)
- Warning PPM (yellow, monitor)
- Critical PPM (red, immediate action)

**Example:**
- Good: ≤ 600 ppm
- Warning: 600-900 ppm
- Critical: > 900 ppm

**API:**
```bash
GET /api/thresholds          # Get your settings
POST /api/thresholds         # Update settings
{
  "good_level": 600,
  "warning_level": 900,
  "critical_level": 1200
}
```

---

## 📈 Feature 5 & 6: Analytics & Visualization

**Where:** Click "📈 Visualisations" in navbar

**What it does:**
- Daily Averages (30-day trend with min/max)
- Period Comparison (week-over-week or month-over-month)
- Heatmap (hourly distribution by day)
- Hourly Trends (7-day area chart)

**How to use:**
1. Navigate to /visualization
2. View daily chart by default
3. Click tabs to switch between views
4. Charts update automatically with your data

**APIs:**
```bash
GET /api/analytics/compare-periods?type=week|month
GET /api/analytics/daily-comparison
```

---

## 🔐 Feature 7: User Roles & Permissions

**Where:** Admin Dashboard > Users

**Admin can grant permissions:**
- **view_reports** - Access analytics dashboards
- **manage_exports** - Create/schedule data exports
- **manage_sensors** - Add/configure sensors
- **manage_alerts** - Create custom alerts
- **manage_users** - Manage other user accounts

**Admin API:**
```bash
# Grant permission
POST /api/permissions/{user_id}/{permission}

# Revoke permission  
DELETE /api/permissions/{user_id}/{permission}

# View user permissions
GET /api/permissions/{user_id}

# View your permissions
GET /api/permissions
```

**Example:**
```bash
# Grant user #42 permission to view reports
POST /api/permissions/42/view_reports

# Remove export permission
DELETE /api/permissions/42/manage_exports
```

---

## 📥 Feature 9: CSV Data Import

**Where:** Admin Dashboard > Maintenance > "📥 Import CO₂ Data"

**What it does:**
- Bulk import historical CO₂ readings from CSV file
- Validates data (PPM range 0-5000, timestamps)
- Shows import statistics and errors

**CSV Format:**
```csv
timestamp,ppm
2024-01-01 08:00:00,412
2024-01-01 09:00:00,418
2024-01-01 10:00:00,425
```

**How to import:**
1. Go to Admin > Maintenance tab
2. Select CSV file (use sample_import.csv as template)
3. Click "Upload & Import"
4. View results and error messages

**API:**
```bash
POST /api/import/csv
Content-Type: multipart/form-data

Response:
{
  "imported": 22,
  "total": 25,
  "errors": ["Row 3: Invalid PPM value 5500"],
  "success": true
}
```

---

## 🛡️ Feature 10: Rate Limiting & Security

**What it does:**
- Protects against brute force attacks
- Prevents abuse of expensive operations
- Enforces security best practices

**Rate Limits:**
| Endpoint | Limit |
|----------|-------|
| Login | 5 per minute |
| Register | 3 per minute |
| Forgot Password | 3 per minute |
| CSV Import | 5 per minute |
| Exports | 10 per minute |

**Security Headers Applied:**
- Content-Security-Policy (prevents XSS)
- Strict-Transport-Security (enforces HTTPS)
- X-Frame-Options (prevents clickjacking)
- X-XSS-Protection (browser XSS filter)

**Error Response (rate limit exceeded):**
```json
HTTP 429 Too Many Requests
{
  "error": "Rate limit exceeded"
}
```

---

## 🔄 Feature Interactions

### CSV Import + Visualization
1. Import CSV data via Admin > Maintenance
2. Visualizations automatically show imported data
3. Historical comparison reflects new readings

### Thresholds + Alerts
1. Set custom thresholds in Settings
2. Alerts triggered based on your levels
3. No configuration needed - automatic

### Permissions + Export
1. Admin grants "manage_exports" permission
2. User can now create and schedule exports
3. Export rate limit protects server

### Security + All Features
1. All endpoints protected by rate limiting
2. All responses include security headers
3. No special configuration needed

---

## 🧪 Test Data

Sample CSV file provided: `sample_import.csv`

Contains 22 valid readings for testing:
- Dates: 2024-01-01 to 2024-01-02
- PPM range: 412-472
- Format: CSV with timestamp and ppm columns

---

## ⚡ Quick Start Checklist

- [ ] Log in as admin user
- [ ] Go to Settings, set custom thresholds
- [ ] Check "📈 Visualisations" dashboard
- [ ] Visit Admin page to see new features
- [ ] Import sample_import.csv to test
- [ ] Grant user permissions as needed
- [ ] Verify rate limiting (try 6 login attempts)
- [ ] Check security headers in browser

---

## 🆘 Troubleshooting

**CSV import fails?**
- ✓ File must be .csv format
- ✓ Must have columns: timestamp, ppm
- ✓ Timestamps must be YYYY-MM-DD HH:MM:SS
- ✓ PPM must be 0-5000

**Visualization not showing data?**
- ✓ Check "view_reports" permission granted
- ✓ Ensure readings exist in database
- ✓ Check browser console for errors

**Permission denied on feature?**
- ✓ Admin must grant specific permission
- ✓ User must log out and log in again
- ✓ Check /api/permissions endpoint

**Rate limit error?**
- ✓ Wait 1-2 minutes to retry
- ✓ Contact admin if limit too strict

---

## 📚 More Information

**Full documentation:**
- FEATURE_IMPLEMENTATION_COMPLETE.md - Comprehensive guide
- AUTH_QUICK_REFERENCE.md - Authentication details
- VERIFICATION_CHECKLIST.md - Testing procedures

**Database functions:**
- database.py (1285+ lines) - All backend logic
- app.py (1610+ lines) - All API routes

**Templates:**
- visualization.html - Interactive dashboard (370+ lines)
- admin.html - Admin panel with CSV import
- settings.html - User settings with thresholds
