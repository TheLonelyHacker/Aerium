# Alerts System Testing Guide

## Overview
The alerts system has been successfully implemented across all pages with:
- 🔔 Alerts button in navbar with badge count
- 📋 Persistent side panel (slides in from right)
- ✕ Click-to-dismiss individual alerts
- ⏱️ Auto-remove after timeout (inherited from toast system)
- 🎨 Color-coded alerts (green=success, yellow=warning, red=error)

## Files Modified
- `templates/base.html` - Added alerts button, panel, and script loading
- `static/css/style.css` - Added navbar button and panel styling (~150 lines)
- `static/js/alerts.js` - NEW file with complete alerts management system
- No changes needed to `utils.js` or `live.js` (already have alert triggering)

## Testing Steps

### 1. Test Alerts Button Click
1. Navigate to http://127.0.0.1:5000/
2. Click the 🔔 button in the navbar
3. **Expected:** Side panel slides in from the right
4. Click the ✕ close button in the panel header
5. **Expected:** Panel slides out to the right

### 2. Test Clicking Outside Panel
1. Click 🔔 button to open panel
2. Click anywhere on the main content area (outside the panel)
3. **Expected:** Panel closes automatically

### 3. Trigger an Alert
1. Navigate to http://127.0.0.1:5000/live
2. Wait for CO2 readings to stream in (via WebSocket)
3. When CO2 exceeds threshold (default 1200 ppm), wait for alert
4. **Expected:** 
   - Badge shows "1" in red circle
   - Panel contains the alert with timestamp
   - Alert is color-coded (yellow for threshold_exceeded, green for recovery)

### 4. Test Alert Dismissal
1. With alert visible in panel, click the ✕ button on the alert item
2. **Expected:**
   - Alert is removed immediately
   - Badge count decrements (or disappears if last alert)
   - "Aucune alerte pour le moment" message shows if no alerts

### 5. Test Multiple Alerts
1. Navigate to /live and wait for multiple CO2 threshold events
2. Each alert should appear in the panel (newest first)
3. Badge should show count (e.g., "3")
4. **Expected:** Alerts are stacked, newest on top

### 6. Test Across Pages
1. Trigger an alert on /live (wait for threshold exceeded)
2. While alert is in panel, navigate to another page (/dashboard, /settings, etc.)
3. **Expected:** Alert persists in panel and navbar badge remains visible
4. Click alerts button again
5. **Expected:** Same alert is still there

### 7. Test Toast Notifications (Auto-remove)
1. On /live page, observe console or look for toast notifications
2. When alert is triggered, toast may appear briefly
3. **Expected:** Toast auto-removes after ~4 seconds
4. Alert remains in panel until manually dismissed or page refresh

## Expected Alert Types
- **threshold_exceeded** → Yellow/warning alert ("CO₂ dépasse le seuil!")
- **recovery** → Green/success alert ("CO₂ revenu à la normale")
- **error** → Red/error alert (rare, system errors)

## File Locations
- **Button & Panel:** [templates/base.html](templates/base.html#L44-L78)
- **Styling:** [static/css/style.css](static/css/style.css#L317-L440)
- **Management:** [static/js/alerts.js](static/js/alerts.js)
- **Integration:** [static/js/utils.js](static/js/utils.js#L411) (dispatchEvent) & [static/js/live.js](static/js/live.js) (triggers)

## Browser DevTools Testing
Open browser console (F12) and test manually:

```javascript
// Manually add an alert to test panel
const event = new CustomEvent('alert-updated', {
  detail: {
    timestamp: new Date(),
    message: 'Test alert message',
    type: 'threshold_exceeded',
    value: 1250
  }
});
window.dispatchEvent(event);
```

## Troubleshooting
- **Panel doesn't open:** Check console (F12) for JavaScript errors, verify alerts.js loaded
- **Badge doesn't show:** Check if alert event is being dispatched (see browser console)
- **Alerts don't persist:** Verify not using incognito mode (session storage), check Flask serving static files
- **Styling looks off:** Hard refresh (Ctrl+Shift+R) to clear CSS cache

## Known Behaviors
- ✅ Alerts limited to 20 maximum (prevents memory issues)
- ✅ Newest alerts appear at top of list
- ✅ Badge hides when no alerts (display: none)
- ✅ Panel closes on outside click or close button
- ✅ Alert timestamps show in local browser time (French format)
- ✅ Alerts are NOT persisted to database (only in current session)

## Next Steps
- Account deletion feature
- Data export with date range
- Dark/light theme toggle
- Multi-day comparison
- Daily/weekly reports
- Email alerts system
