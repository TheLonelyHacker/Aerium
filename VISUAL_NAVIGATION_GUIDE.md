# Visual Reference: Feature Locations & Navigation

## 🗺️ Where to Find Everything

### Navigation Map

```
├── Home Page (Overview)
├── 📊 Analytics
├── 🔴 Live Monitor
├── ⚙️ Settings
│   ├── Profile Settings
│   ├── Email Notification
│   ├── Thresholds [🆕 FEATURE 4]
│   ├── Security
│   └── Export Data
├── 📈 Visualisations [🆕 FEATURE 6]
│   ├── Daily Averages Chart
│   ├── Period Comparison Chart
│   ├── Heatmap
│   └── Hourly Trends
├── 📖 Guide
├── 👤 Profile
└── 🔧 Admin [🆕 FEATURE 7, 9]
    ├── Overview Tab
    │   └── System Statistics
    ├── Users Tab
    │   ├── User List
    │   ├── Grant/Revoke Permissions [FEATURE 7]
    │   └── Delete Users
    ├── Maintenance Tab
    │   ├── 🗑️ Cleanup Old CO₂ Data
    │   ├── 📋 Cleanup Audit Logs
    │   ├── 🔐 Cleanup Login History
    │   └── 📥 Import CO₂ Data [🆕 FEATURE 9]
    └── Audit Logs Tab
        └── Audit Event History
```

---

## Feature 4: Custom Thresholds

### UI Location
**Settings > Thresholds section**

### What You'll See
```
┌─────────────────────────────────────┐
│ ⚠️ Threshold Settings               │
├─────────────────────────────────────┤
│ Green (Good): [====|====] 600 ppm   │
│ Yellow (Warning): [===|=====] 900   │
│ Red (Critical): [==|======] 1200    │
│ [SAVE THRESHOLDS]                   │
└─────────────────────────────────────┘
```

### Related Elements
- Status indicator colors:
  - 🟢 Green = below good_level
  - 🟡 Yellow = between good and warning
  - 🔴 Red = above critical_level

---

## Feature 5 & 6: Visualization Dashboard

### UI Location
**Click "📈 Visualisations" in top navigation**

### Dashboard Layout
```
┌──────────────────────────────────────────────────┐
│ 📈 CO₂ Analytics Dashboard                       │
├──────────────────────────────────────────────────┤
│ [Daily Avg] [Comparison] [Heatmap] [Hourly]     │
├──────────────────────────────────────────────────┤
│                                                  │
│  📊 Chart Display Area                          │
│  ┌─────────────────────────────────────────┐   │
│  │ Line chart with min/max bands           │   │
│  │ Data points show PPM values             │   │
│  │ Legend shows colors                     │   │
│  └─────────────────────────────────────────┘   │
│                                                  │
│  Statistics Cards:                             │
│  ┌──────────┬──────────┬──────────┐            │
│  │ Current  │ Average  │ Max      │            │
│  │ 820 ppm  │ 750 ppm  │ 950 ppm  │            │
│  └──────────┴──────────┴──────────┘            │
└──────────────────────────────────────────────────┘
```

### 4 Chart Types

**1. Daily Averages (Default)**
- Shows 30-day trend
- Line chart with min/max bands
- Color-coded severity
- Statistics cards below

**2. Period Comparison**
- Week-over-week or month-over-month
- Bar chart showing current vs previous
- Percentage change indicator
- Period selector dropdown

**3. Heatmap**
- Hourly distribution across 7 days
- Color intensity = PPM level
- Green (good) → Yellow (warning) → Red (critical)
- Grid layout (7 rows = days)

**4. Hourly Trends**
- 7-day area chart
- Shows hourly PPM levels
- Shaded region under line
- Legend with date/time

---

## Feature 7: User Permissions

### UI Location
**Admin Dashboard > Users Tab**

### What You'll See
```
┌─────────────────────────────────────┐
│ 👥 User Management                  │
├─────────────────────────────────────┤
│ Username   | Role  | Permissions |  │
│ john_doe   | User  | view_reports|  │
│ jane_smith | Admin | ALL         |  │
│ bob_wilson | User  | [Grant ▼]   |  │
└─────────────────────────────────────┘
```

### Permission Types
1. **view_reports** - Access analytics & dashboards
2. **manage_exports** - Create & schedule exports
3. **manage_sensors** - Configure sensor settings
4. **manage_alerts** - Create custom alerts
5. **manage_users** - Manage user accounts (admin)

### How to Grant/Revoke
1. Go to Admin > Users tab
2. Find user in list
3. Click permission dropdown
4. Select permission to grant
5. Confirm action

---

## Feature 9: CSV Data Import

### UI Location
**Admin Dashboard > Maintenance Tab > "📥 Import CO₂ Data"**

### What You'll See
```
┌──────────────────────────────────────────┐
│ 📥 Import CO₂ Data (CSV)                 │
├──────────────────────────────────────────┤
│ Format: timestamp, ppm                   │
│ [Select File Button]                     │
│ [Upload & Import Button]                 │
│                                          │
│ Results Area (after import):             │
│ ✅ Success! 22/25 readings imported.     │
│ ⚠️ Row 3: Invalid PPM value 5500         │
│ ⚠️ Row 7: Missing timestamp              │
└──────────────────────────────────────────┘
```

### CSV Format Required
```csv
timestamp,ppm
2024-01-01 08:00:00,412
2024-01-01 09:00:00,418
2024-01-01 10:00:00,425
```

### Import Process
1. Prepare CSV file (use sample_import.csv as template)
2. Go to Admin > Maintenance
3. Click "Select File"
4. Choose your CSV file
5. Click "Upload & Import"
6. Review results and error messages

---

## Feature 10: Rate Limiting & Security

### What Users See

**When Rate Limit Exceeded:**
```json
HTTP 429 Too Many Requests
{
  "error": "Rate limit exceeded. Please try again later."
}
```

### Rate Limit Indicators
| Action | Limit | Message |
|--------|-------|---------|
| Login attempts | 5/min | Wait before retrying |
| Register | 3/min | Account creation throttled |
| CSV Import | 5/min | Import limit reached |
| Data Export | 10/min | Export limit reached |

### Security Indicators
- 🔒 HTTPS enforced (HSTS header)
- 🛡️ XSS protection enabled
- ☑️ CSRF tokens validated
- 🔑 Secure cookies used
- 📋 CSP headers active

---

## Quick Navigation Paths

### Access Settings Thresholds
```
Home → Settings (⚙️) → Thresholds → [Adjust sliders] → Save
```

### View Visualization Dashboard
```
Home → Visualisations (📈) → [Select chart type]
```

### Import CSV Data
```
Home → Admin (🔧) → Maintenance Tab → Import CO₂ Data → [Select file]
```

### Manage User Permissions
```
Home → Admin (🔧) → Users Tab → [Select user] → Grant Permission
```

### Configure Custom Alerts
```
Home → Settings (⚙️) → Thresholds → [Set levels]
(Automatically applies to all CO₂ readings)
```

---

## Color Coding Reference

### Status Colors
- 🟢 **Green (Good)** - PPM ≤ good_level (default: 600)
- 🟡 **Yellow (Warning)** - good_level < PPM < critical_level
- 🔴 **Red (Critical)** - PPM ≥ critical_level (default: 1200)

### UI Element Colors
- 🔵 **Blue** - Primary actions, information
- 🟢 **Green** - Success, confirm actions
- 🟡 **Yellow** - Warnings, pending actions
- 🔴 **Red** - Errors, dangerous actions

### Chart Colors
- **Daily Averages:** Blue line with light blue band
- **Comparison:** Blue (current) vs Gray (previous)
- **Heatmap:** Green → Yellow → Red gradient
- **Hourly Trends:** Green shaded area

---

## Mobile Navigation

### Hamburger Menu
```
Home → ☰ Menu
       ├── Home
       ├── Analytics
       ├── Live
       ├── Settings
       ├── Visualizations
       ├── Guide
       └── Admin (if admin)
```

### Responsive Design
- Touch-friendly buttons
- Swipe between chart tabs
- Vertical layout on small screens
- Optimized for mobile viewing

---

## Keyboard Shortcuts (Future Enhancement)

### Planned Shortcuts
- `V` - View Visualizations
- `S` - Settings
- `A` - Admin
- `T` - Thresholds
- `L` - Live Monitor
- `?` - Help/Keyboard Shortcuts

---

## Responsive Breakpoints

### Desktop (>1024px)
- Full navigation visible
- Side-by-side layouts
- All charts visible
- Admin tabs visible

### Tablet (768-1024px)
- Hamburger menu hidden
- Stacked layouts
- 2-column grids
- Optimized touch targets

### Mobile (<768px)
- Full hamburger menu
- Single column layout
- Vertical charts
- Large buttons for touch

---

## Feature Summary Card

```
╔════════════════════════════════════════════════════╗
║             PHASE 5 FEATURES SUMMARY               ║
╠════════════════════════════════════════════════════╣
║ ✅ Feature 4: Custom Thresholds & Rules           ║
║    Location: Settings > Thresholds                ║
║    Status: COMPLETE                               ║
├────────────────────────────────────────────────────┤
║ ✅ Feature 5: Historical Comparison Analytics     ║
║    Location: Visualisations > Comparison Tab      ║
║    Status: COMPLETE                               ║
├────────────────────────────────────────────────────┤
║ ✅ Feature 6: Data Visualization Dashboard        ║
║    Location: Visualisations (📈 link)             ║
║    Status: COMPLETE                               ║
├────────────────────────────────────────────────────┤
║ ✅ Feature 7: User Roles & Permissions            ║
║    Location: Admin > Users Tab                    ║
║    Status: COMPLETE                               ║
├────────────────────────────────────────────────────┤
║ ✅ Feature 9: CSV Data Import                     ║
║    Location: Admin > Maintenance Tab              ║
║    Status: COMPLETE                               ║
├────────────────────────────────────────────────────┤
║ ✅ Feature 10: Rate Limiting & Security           ║
║    Location: Global (all endpoints)               ║
║    Status: COMPLETE                               ║
╚════════════════════════════════════════════════════╝
```

---

## Need Help?

### Feature Questions
1. Check FEATURES_QUICK_REFERENCE.md
2. Review FEATURE_IMPLEMENTATION_COMPLETE.md
3. Look for inline code comments

### CSV Import Questions
1. Use sample_import.csv as template
2. Verify CSV format: timestamp, ppm
3. Check PPM range (0-5000)

### Permission Issues
1. Verify admin status
2. Check permission with API endpoint
3. Ensure user logged out/in after permission grant

### Technical Questions
1. Check code comments in app.py
2. Review database.py for function signatures
3. See PHASE5_COMPLETION_REPORT.md for technical details

---

**Complete Navigation & Reference Guide**  
**For: Aerium CO₂ Monitoring Platform v5.0**
