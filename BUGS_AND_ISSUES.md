# Morpheus CO₂ Webapp - Bugs & Issues Report

## 🔴 CRITICAL ISSUES

### 1. **Hardcoded Secret Key** (Security Risk)
**File:** [app.py](app.py#L26)
```python
app.config['SECRET_KEY'] = 'morpheus-co2-secret-key'
```
**Issue:** The SECRET_KEY is hardcoded and exposed in the repository. This is a major security vulnerability.
**Fix:** Use environment variables:
```python
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
```

---

### 2. **Debug Mode Enabled in Production** (Security Risk)
**File:** [app.py](app.py#L913)
```python
socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
```
**Issue:** Running with `debug=True` and `allow_unsafe_werkzeug=True` exposes the debugger to the public network (0.0.0.0).
**Fix:**
```python
debug_mode = os.getenv('FLASK_ENV') == 'development'
socketio.run(app, debug=debug_mode, host='127.0.0.1', port=5000)
```

---

### 3. **Email Service Not Configured But Expected** (Feature Broken)
**File:** [app.py](app.py#L45-L55)
- Email verification claims to work but returns `True` immediately without sending
- Password reset emails don't actually send
- `mail` object referenced but never imported or initialized

**Issue:** Users can't verify emails or reset passwords properly
**Fix:** Either implement Flask-Mail properly or remove email-dependent features

---

### 4. **Duplicate Code & Dead Routes**
**File:** [app.py](app.py#L472-L474)
```python
return render_template("profile.html", user=user, settings=user_settings)
```
This line appears after a return statement in the `change_password` function (dead code)

---

## 🟠 HIGH PRIORITY ISSUES

### 5. **CORS Misconfiguration** (Security Risk)
**File:** [app.py](app.py#L37)
```python
socketio = SocketIO(app, cors_allowed_origins="*")
```
**Issue:** Allows any origin to connect to your WebSocket. Should restrict to specific domains.
**Fix:**
```python
cors_allowed_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
socketio = SocketIO(app, cors_allowed_origins=cors_allowed_origins)
```

---

### 6. **Missing Input Validation on API Routes**
**File:** [app.py](app.py#L721-L730)
```python
@app.route("/api/cleanup", methods=["POST"])
def api_cleanup():
    days = request.json.get("days", 90) if request.json else 90
    # NO VALIDATION on 'days' value
```
**Issue:** User can pass negative numbers or extremely large values
**Fix:**
```python
days = int(request.json.get("days", 90))
if days < 1 or days > 365:
    return jsonify({'error': 'Days must be between 1 and 365'}), 400
```

---

### 7. **Missing Login Required on API Routes**
**File:** [app.py](app.py#L567-L570), [app.py](app.py#L605-L610)
```python
@app.route("/api/history/<range>")
def history_range(range):  # NO @login_required
```
**Issue:** Unauthorized users can access CO₂ history data
**Fix:** Add `@login_required` decorator to all API endpoints that return user data

---

### 8. **No Rate Limiting**
**Issue:** API endpoints like `/api/latest`, `/api/history/*` have no rate limiting, allowing DOS attacks
**Fix:** Implement rate limiting with Flask-Limiter:
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route("/api/latest")
@limiter.limit("100/hour")
def api_latest():
    ...
```

---

## 🟡 MEDIUM PRIORITY ISSUES

### 9. **Global Variables for CO₂ State Not Thread-Safe**
**File:** [fake_co2.py](../app/fake_co2.py) (not shown but referenced)
**Issue:** Background broadcast thread and multiple API calls may race on global state
**Fix:** Use thread locks or database-backed state

---

### 10. **Database Connections Not Always Closed**
**File:** [app.py](app.py#L517-L525)
```python
@app.route("/api/history/<range>")
def history_range(range):
    db = get_db()
    if range == "today":
        rows = db.execute(...)
    elif range == "7d":
        ...
    else:
        db.close()  # Only closed in error case!
        return jsonify({"error": ...}), 400
    # Missing db.close() for success paths
```
**Issue:** Database connections leak on successful requests
**Fix:** Use context managers or try/finally:
```python
db = get_db()
try:
    if range == "today":
        rows = db.execute(...)
    # ... rest of logic
finally:
    db.close()
```

---

### 11. **Weak Password Requirements**
**File:** [app.py](app.py#L345), [app.py](app.py#L262)
```python
if len(password) < 6:
    return render_template("register.html", error="Le mot de passe doit contenir au moins 6 caractères")
```
**Issue:** Only 6 characters minimum. No complexity requirements.
**Fix:** Enforce stronger requirements (uppercase, digits, symbols)

---

### 12. **No HTTPS Enforcement**
**Issue:** No redirect from HTTP to HTTPS, no HSTS headers
**Fix:**
```python
@app.before_request
def enforce_https():
    if not request.is_secure and not app.debug:
        return redirect(request.url.replace('http://', 'https://'), code=301)
```

---

### 13. **SQL Query Using Invalid Date Function**
**File:** [app.py](app.py#L572-L574)
```python
WHERE date(timestamp) = date('now')
```
**Issue:** SQLite's `date('now')` returns UTC date, but timestamps might be in local timezone
**Fix:** Be explicit:
```python
WHERE date(timestamp, 'localtime') = date('now', 'localtime')
```

---

### 14. **Session Fixation Risk**
**File:** [app.py](app.py#L381-L391)
```python
if remember_me:
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)
```
**Issue:** Session ID not regenerated after login
**Fix:**
```python
session.clear()  # Clear old session
session['user_id'] = user['id']
session['username'] = user['username']
session.regenerate()  # Regenerate session ID
```

---

## 🟢 LOW PRIORITY ISSUES

### 15. **Inconsistent Error Handling**
**Issue:** Mix of returning `jsonify()`, `render_template()`, and HTML directly
**Fix:** Create standardized error response function

---

### 16. **WebSocket Broadcast Without Permission Check**
**File:** [app.py](app.py#L849-L870)
```python
@socketio.on('settings_change')
def handle_settings_change(data):
    socketio.emit('settings_update', data)  # No user check
```
**Issue:** Any connected user can broadcast fake settings to all clients
**Fix:** Add authentication check:
```python
@socketio.on('settings_change')
def handle_settings_change(data):
    if 'user_id' not in session:
        return False
    # ...
```

---

### 17. **Missing CSRF Protection**
**File:** All forms in templates
**Issue:** No CSRF tokens on POST forms
**Fix:** Use Flask-WTF:
```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

---

### 18. **No Logging for Security Events**
**Issue:** No audit trail for admin actions, password changes, etc.
**Fix:** Add logging module:
```python
import logging
logging.basicConfig(filename='security.log', level=logging.INFO)
```

---

### 19. **Incomplete Admin User Management**
**File:** [app.py](app.py#L508-L516)
```python
@app.route("/admin/user/<int:user_id>/role/<role>", methods=["POST"])
@admin_required
def update_user_role(user_id, role):
    # No endpoint to create new admins
    # No endpoint to delete users
```

---

### 20. **JavaScript: Missing Error Handling in Async Operations**
**File:** [static/js/live.js](static/js/live.js) and others
**Issue:** fetch() calls without `.catch()` - unhandled promise rejections
**Fix:**
```javascript
fetch('/api/latest')
  .then(r => r.json())
  .catch(err => console.error('API Error:', err));
```

---

## 📋 CHECKLIST FOR FIXES

- [ ] Move SECRET_KEY to environment variable
- [ ] Disable debug mode in production
- [ ] Configure or remove email features
- [ ] Add @login_required to all data-returning API endpoints
- [ ] Add rate limiting to APIs
- [ ] Fix database connection leaks
- [ ] Add CSRF protection
- [ ] Implement CORS whitelist
- [ ] Add HTTPS enforcement
- [ ] Fix session regeneration on login
- [ ] Add input validation to all API endpoints
- [ ] Implement audit logging
- [ ] Add WebSocket authentication
- [ ] Strengthen password requirements
- [ ] Remove dead/duplicate code

---

## 🚀 PRIORITY ORDER TO FIX

1. ✅ Secret Key (security)
2. ✅ Debug mode (security)
3. ✅ CORS configuration (security)
4. ✅ Login required on APIs (security)
5. ✅ Rate limiting (security)
6. ✅ Database connection leaks (stability)
7. ✅ Email configuration (functionality)
8. ✅ Input validation (stability)
9. ✅ CSRF protection (security)
10. ✅ HTTPS enforcement (security)
