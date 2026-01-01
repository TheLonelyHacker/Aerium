from flask import Flask, jsonify, render_template, request, make_response
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import time
from datetime import datetime, date
import os
from database import get_db, init_db
import json
from flask import send_file
import io
from weasyprint import HTML
import threading

from fake_co2 import generate_co2, save_reading, reset_state
from database import cleanup_old_data


app = Flask(__name__)
app.config['SECRET_KEY'] = 'morpheus-co2-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

init_db()

def load_settings():
    db = get_db()
    rows = db.execute("SELECT key, value FROM settings").fetchall()
    db.close()

    settings = DEFAULT_SETTINGS.copy()
    for r in rows:
        settings[r["key"]] = json.loads(r["value"])

    return settings

print("=" * 50)
print(f"Current directory: {os.getcwd()}")
print(f"Template folder exists: {os.path.exists('templates')}")
if os.path.exists('templates'):
    print(f"Files in templates/: {os.listdir('templates')}")
print("=" * 50)

DEFAULT_SETTINGS = {
    "analysis_running": True,
    "good_threshold": 800,
    "bad_threshold": 1200,
    "alert_threshold": 1400,
    "realistic_mode": True,
    "update_speed": 1,
    "overview_update_speed": 5,
}

def save_settings(data):
    db = get_db()
    for k, v in data.items():
        db.execute(
            "REPLACE INTO settings (key, value) VALUES (?, ?)",
            (k, json.dumps(v))
        )
    db.commit()
    db.close()

# 1. ROOT ROUTE - DASHBOARD (MUST BE FIRST!)
@app.route("/")
def index():
    return render_template("index.html")  # Dashboard page

@app.route("/live")
def live_page():
    return render_template("live.html")  # Settings page

# 2. SETTINGS ROUTE
@app.route("/settings")
def settings_page():
    return render_template("settings.html")  # Settings page

@app.route("/analytics")
def analytics():
    return render_template("analytics.html")

@app.route("/api/history/<range>")
def history_range(range):
    db = get_db()

    if range == "today":
        rows = db.execute("""
            SELECT ppm, timestamp
            FROM co2_readings
            WHERE date(timestamp) = date('now')
            ORDER BY timestamp
        """).fetchall()

    elif range == "7d":
        rows = db.execute("""
            SELECT ppm, timestamp
            FROM co2_readings
            WHERE timestamp >= datetime('now', '-7 days')
            ORDER BY timestamp
        """).fetchall()

    elif range == "30d":
        rows = db.execute("""
            SELECT ppm, timestamp
            FROM co2_readings
            WHERE timestamp >= datetime('now', '-30 days')
            ORDER BY timestamp
        """).fetchall()

    else:
        db.close()
        return jsonify({"error": "Invalid range"}), 400

    db.close()
    return jsonify([dict(r) for r in rows])

# 3. API ROUTES
@app.route("/api/latest")
def api_latest():
    settings = load_settings()

    if not settings["analysis_running"]:
        resp = make_response(jsonify({
            "analysis_running": False,
            "ppm": None
        }))
        resp.headers["Cache-Control"] = "no-store"
        return resp

    ppm = generate_co2(settings["realistic_mode"])
    save_reading(ppm)

    resp = make_response(jsonify({
        "analysis_running": True,
        "ppm": ppm,
        "timestamp": datetime.utcnow().isoformat()
    }))
    resp.headers["Cache-Control"] = "no-store"
    return resp

@app.route("/api/history/today")
def api_history_today():
    db = get_db()
    rows = db.execute("""
        SELECT ppm, timestamp
        FROM co2_readings
        WHERE date(timestamp) = date('now')
        ORDER BY timestamp
    """).fetchall()
    db.close()

    return jsonify([dict(r) for r in rows])

def get_today_history():
    db = get_db()
    rows = db.execute("""
        SELECT ppm, timestamp
        FROM co2_readings
        WHERE date(timestamp) = date('now')
        ORDER BY timestamp
    """).fetchall()
    db.close()

    return [dict(r) for r in rows]


@app.route("/api/settings", methods=["GET", "POST", "DELETE"])
def api_settings():
    if request.method == "POST":
        save_settings(request.json)
        return jsonify({"status": "ok"})

    if request.method == "DELETE":
        db = get_db()
        db.execute("DELETE FROM settings")
        db.commit()
        db.close()
        
        # Broadcast reset to all WebSocket clients
        socketio.emit('settings_update', DEFAULT_SETTINGS)
        
        return jsonify(DEFAULT_SETTINGS)
        return jsonify(DEFAULT_SETTINGS)

    return jsonify(load_settings())

@app.route("/api/history/latest/<int:limit>")
def api_history_latest(limit):
    db = get_db()
    rows = db.execute("""
        SELECT id, ppm, timestamp
        FROM co2_readings
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()
    db.close()

    # reverse so oldest → newest
    return jsonify([dict(r) for r in reversed(rows)])

@app.route("/api/cleanup", methods=["POST"])
def api_cleanup():
    """Clean up old CO₂ readings (default: 90 days)"""
    days = request.json.get("days", 90) if request.json else 90
    deleted = cleanup_old_data(days)
    return jsonify({"status": "ok", "deleted": deleted, "days": days})

@app.route("/api/reset-state", methods=["POST"])
def api_reset_state():
    """Reset CO₂ generator state"""
    base = request.json.get("base", 600) if request.json else 600
    reset_state(base)
    return jsonify({"status": "ok", "base": base})


def generate_pdf(html):
    pdf_io = io.BytesIO()

    HTML(
        string=html,
        base_url=os.path.abspath(".")
    ).write_pdf(
        target=pdf_io,
        presentational_hints=True
    )

    pdf_io.seek(0)

    return send_file(
        pdf_io,
        mimetype="application/pdf",
        as_attachment=False,
        download_name="daily_report.pdf"
    )


@app.route("/api/report/daily/pdf")
def export_daily_pdf():
    data = get_today_history()
    settings = load_settings()

    if not data:
        return "No data", 400

    values = [d["ppm"] for d in data]

    avg = round(sum(values) / len(values))
    max_ppm = max(values)
    min_ppm = min(values)

    # ⏱ minutes above bad threshold
    bad_minutes = sum(1 for v in values if v >= settings["bad_threshold"])

    # ✅ EXPOSURE BREAKDOWN (THIS IS YOUR QUESTION)
    good = sum(1 for v in values if v < settings["good_threshold"])
    medium = sum(
        1 for v in values
        if settings["good_threshold"] <= v < settings["bad_threshold"]
    )
    bad = sum(1 for v in values if v >= settings["bad_threshold"])
    total = len(values)

    good_pct = round(good / total * 100)
    medium_pct = round(medium / total * 100)
    bad_pct = round(bad / total * 100)

    with open("static/css/report.css", "r", encoding="utf-8") as f:
        report_css = f.read()

    html = render_template(
        "report_daily.html",
        date=date.today().strftime("%d %B %Y"),
        avg=avg,
        max=max_ppm,
        min=min_ppm,
        bad_minutes=bad_minutes,
        good_pct=good_pct,
        medium_pct=medium_pct,
        bad_pct=bad_pct,
        good_threshold=settings["good_threshold"],
        bad_threshold=settings["bad_threshold"],
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        report_css=report_css
    )

    return generate_pdf(html)


# ================================================================================
#                          WEBSOCKET HANDLERS
# ================================================================================

# Global state for WebSocket broadcasting
broadcast_thread = None
broadcast_running = False

@socketio.on('connect')
def handle_connect():
    """Handle client connection to WebSocket"""
    print(f"Client connected")
    emit('status', {'data': 'Connected to Morpheus CO₂ Monitor'})
    
    # Send current settings to client
    settings = load_settings()
    emit('settings_update', settings)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected")

@socketio.on('request_data')
def handle_request_data():
    """Handle request for latest CO₂ data"""
    settings = load_settings()
    
    if not settings["analysis_running"]:
        emit('co2_update', {
            'analysis_running': False,
            'ppm': None,
            'timestamp': datetime.utcnow().isoformat()
        })
        return
    
    ppm = generate_co2(settings["realistic_mode"])
    save_reading(ppm)
    
    emit('co2_update', {
        'analysis_running': True,
        'ppm': ppm,
        'timestamp': datetime.utcnow().isoformat()
    })

@socketio.on('settings_change')
def handle_settings_change(data):
    """Handle settings update and broadcast to all clients"""
    save_settings(data)
    # Broadcast to all clients
    socketio.emit('settings_update', data)

def broadcast_co2_loop():
    """Background thread that broadcasts CO₂ readings to all connected clients"""
    global broadcast_running
    broadcast_running = True
    last_ppm = None
    last_analysis_state = None
    
    while broadcast_running:
        settings = load_settings()
        
        if settings["analysis_running"]:
            ppm = generate_co2(settings["realistic_mode"])
            save_reading(ppm)
            
            # Only broadcast if value changed significantly (>= 5 ppm) or state changed
            if last_ppm is None or abs(ppm - last_ppm) >= 5 or last_analysis_state != True:
                socketio.emit('co2_update', {
                    'analysis_running': True,
                    'ppm': ppm,
                    'timestamp': datetime.utcnow().isoformat()
                }, to=None)
                last_ppm = ppm
                last_analysis_state = True
        else:
            # Only broadcast state change once
            if last_analysis_state != False:
                socketio.emit('co2_update', {
                    'analysis_running': False,
                    'ppm': None,
                    'timestamp': datetime.utcnow().isoformat()
                }, to=None)
                last_analysis_state = False
        
        # Respect update_speed setting (default 1 second)
        update_delay = settings.get("update_speed", 1)
        time.sleep(update_delay)

def start_broadcast_thread():
    """Start the background broadcast thread"""
    global broadcast_thread, broadcast_running
    if broadcast_thread is None or not broadcast_thread.is_alive():
        broadcast_running = True
        broadcast_thread = threading.Thread(target=broadcast_co2_loop, daemon=True)
        broadcast_thread.start()
        print("[OK] WebSocket broadcast thread started")

def stop_broadcast_thread():
    """Stop the background broadcast thread"""
    global broadcast_running
    broadcast_running = False
    print("[OK] WebSocket broadcast thread stopped")




if __name__ == "__main__":
    start_broadcast_thread()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)