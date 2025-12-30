# Aerium - AI Coding Assistant Guidelines

**Aerium** is a real-time air quality monitoring dashboard built with Flask that tracks CO₂ levels and generates insights through an interactive web interface.

## Architecture Overview

### Backend Stack
- **Framework:** Flask (Python)
- **Database:** SQLite (`data/aerium.sqlite`) with two tables:
  - `co2_readings`: stores timestamp + ppm values (auto-generated via `fake_co2.py`)
  - `settings`: persisted configuration key-value pairs (JSON values)
- **Data Flow:** `/api/latest` → `generate_co2()` → `save_reading()` → database

### Frontend Architecture
- **Templates:** Jinja2 (`templates/`) extends `base.html` with navbar + content blocks
- **Pages:** index.html (overview), live.html (real-time chart), settings.html, analytics.html
- **Styling:** `static/css/style.css` + page-specific CSS (report.css for PDF exports)
- **JS:** Global state management in `main.js` (899 lines) + page-specific logic in `analytics.js`, `settings.js`

### Data Flow Pattern
1. **Frontend polls** `/api/latest` every N seconds (configurable via `update_speed` setting)
2. **Backend** calls `generate_co2(realistic_mode)` and saves to SQLite
3. **Thresholds** categorize readings: good (<800ppm), medium (800-1200), bad (≥1200)
4. **PDF reports** render via WeasyPrint + Jinja2 templates with exposure breakdowns

## Key Patterns & Conventions

### Settings Management
Settings are loaded on-demand from database (`load_settings()`) and cached locally in JS. The `realistic_mode` toggle switches between drift-based (realistic) vs random (chaos) CO₂ generation. Always reset settings to `DEFAULT_SETTINGS` on DELETE.

### Chart & Real-Time Updates
- **Chart Library:** Chart.js with annotation/zoom plugins (in `base.html`)
- **Max Points:** Limited to 25 points in memory to prevent DOM bloat
- **Color Coding:** Hardcoded in `main.js` (red=bad, yellow=medium, green=good) — must match CSS variables if styling updates
- **Animation:** Uses `easeOutCubic()` for PPM transitions

### Date/Time Conventions
- SQLite uses `CURRENT_TIMESTAMP` for readings (server time)
- History queries use `date('now')` for "today" and `datetime('now', '-X days')` for ranges
- Reports format dates as `"%d %B %Y"` (e.g., "30 December 2025")

### PDF Report Generation
Routes `/api/report/daily/pdf`:
1. Fetches today's readings via `get_today_history()`
2. Calculates stats: avg, max, min, bad_minutes, exposure breakdown (good/medium/bad %)
3. Passes context to `report_daily.html` + injected CSS from `report.css`
4. Returns PDF via WeasyPrint (ensure `base_url` is absolute for image rendering)

## Critical Implementation Details

### Database
- `DB_PATH = Path("data/aerium.sqlite")` — ensure `data/` directory exists
- Always close DB connections with `db.close()` after queries
- Use `row_factory = sqlite3.Row` for dict-like access to rows

### API Response Format
- Always include `"Cache-Control": "no-store"` header on `/api/latest` to prevent browser caching stale readings
- History endpoints return JSON list of dicts with `{id, ppm, timestamp}` structure

### Frontend State Sync
- **Nav status indicator** (`#nav-analysis`) displays `analysis_running` boolean from settings
- **Page detection:** `isLivePage` checks for DOM elements; use similar pattern for page-specific logic
- **Settings POST** sends JSON body; DELETE resets to defaults

## Common Workflows

### Adding a New Setting
1. Add key + default value to `DEFAULT_SETTINGS` dict
2. Load/save logic in `load_settings()` / `save_settings()` handles JSON serialization automatically
3. Frontend: POST to `/api/settings` with `{key: value}` payload

### Extending Reports
- Template: `templates/report_daily.html` receives context from `export_daily_pdf()` route
- CSS: Modify `static/css/report.css` and inject via `render_template(..., report_css=f.read())`
- Metrics: Add calculations before template render (avg/max/min pattern in export_daily_pdf)

### Modifying Thresholds
- Three thresholds live in `DEFAULT_SETTINGS`: `good_threshold` (800), `bad_threshold` (1200), `alert_threshold` (1400)
- Frontend JS polls `/api/settings` to stay in sync; reload page if threshold changes for chart redraw

## File Organization
```
app.py              → Flask routes + settings logic
database.py         → SQLite setup & connection
fake_co2.py         → Data generation (realistic vs random modes)
templates/          → Jinja2 templates (all extend base.html)
static/css/         → Styling (style.css is global, report.css for exports)
static/js/          → main.js (global state), page-specific modules
```

## Testing & Debugging
- **DB state:** Run `check_db.py` to inspect readings and settings tables
- **API responses:** Use browser DevTools → Network tab to inspect `/api/latest`, `/api/history/*` payloads
- **Settings sync:** Clear browser cache if settings appear stale; always POST to `/api/settings` after changes
- **Run server:** `python app.py` starts on `http://0.0.0.0:5000` (accessible from any IP)
