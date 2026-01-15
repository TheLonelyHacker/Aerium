"""
Analytics Blueprint
Handles all CO₂ analytics, reporting, and trend analysis routes
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from database import get_db
from utils.auth_decorators import login_required
from utils.cache import TTLCache
from flask import current_app

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

# Helper functions
def resolve_source_param(allow_sim=True, allow_import=True):
    """Resolve which data source to use (live, simulator, or imported)"""
    db_source = request.args.get('source', 'live')
    
    if db_source == 'simulator' and not allow_sim:
        return 'live'
    if db_source == 'import' and not allow_import:
        return 'live'
    
    return db_source


def build_source_filter(db_source):
    """Build SQL filter clause for data source"""
    if db_source == 'simulator':
        return "source = 'simulator'", []
    elif db_source == 'import':
        return "source = 'import'", []
    else:
        return "source = 'live'", []


# ==================== ROUTE HANDLERS ====================

@analytics_bp.route('/weekcompare', methods=['GET'])
@login_required
def week_compare():
    """Compare current week vs previous week"""
    db_source = resolve_source_param(allow_sim=True, allow_import=True)
    source_clause, source_params = build_source_filter(db_source)
    
    cache = getattr(current_app, '_ttl_cache', None)
    if cache is None:
        cache = TTLCache()
        setattr(current_app, '_ttl_cache', cache)
    
    def load_data():
        db = get_db()
        
        current_week = db.execute(f"""
            SELECT DATE(timestamp) as date, AVG(ppm) as avg_ppm, MAX(ppm) as max_ppm, MIN(ppm) as min_ppm, COUNT(*) as count
            FROM co2_readings
            WHERE timestamp >= datetime('now', '-7 days')
            AND {source_clause}
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, source_params).fetchall()
        
        prev_week = db.execute(f"""
            SELECT DATE(timestamp) as date, AVG(ppm) as avg_ppm, MAX(ppm) as max_ppm, MIN(ppm) as min_ppm, COUNT(*) as count
            FROM co2_readings
            WHERE timestamp >= datetime('now', '-14 days') AND timestamp < datetime('now', '-7 days')
            AND {source_clause}
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, source_params).fetchall()
        
        db.close()
        return {
            'current_week': [dict(row) for row in current_week],
            'previous_week': [dict(row) for row in prev_week]
        }
    
    key = f"weekcompare:{db_source}"
    result = cache.cached(key, ttl_seconds=60, loader=load_data)
    return jsonify(result)


@analytics_bp.route('/trend', methods=['GET'])
@login_required
def analytics_trend():
    """Get trend analysis (rising/stable/falling)"""
    db_source = resolve_source_param(allow_sim=True, allow_import=True)
    source_clause, source_params = build_source_filter(db_source)
    
    cache = getattr(current_app, '_ttl_cache', None)
    if cache is None:
        cache = TTLCache()
        setattr(current_app, '_ttl_cache', cache)
    
    def load_data():
        db = get_db()
        
        if db_source == 'import':
            data = db.execute(f"""
                SELECT 
                    strftime('%Y-%m-%d %H:00', timestamp) as hour,
                    AVG(ppm) as avg_ppm,
                    COUNT(*) as readings
                FROM co2_readings
                WHERE {source_clause}
                GROUP BY hour
                ORDER BY hour DESC
                LIMIT 168
            """, source_params).fetchall()
        else:
            data = db.execute(f"""
                SELECT 
                    strftime('%Y-%m-%d %H:00', timestamp) as hour,
                    AVG(ppm) as avg_ppm,
                    COUNT(*) as readings
                FROM co2_readings
                WHERE timestamp >= datetime('now', '-7 days')
                AND {source_clause}
                GROUP BY hour
                ORDER BY hour DESC
                LIMIT 168
            """, source_params).fetchall()
        
        db.close()
        return data
    
    key = f"trend:{db_source}"
    data = cache.cached(key, ttl_seconds=60, loader=load_data)
    
    if len(data) < 2:
        return jsonify({'trend': 'insufficient_data', 'data': []})
    
    recent_avg = sum(d['avg_ppm'] for d in data[:24]) / min(24, len(data))
    older_data = data[24:48]
    
    if len(older_data) == 0:
        return jsonify({
            'trend': 'insufficient_data',
            'recent_avg': round(recent_avg, 1),
            'older_avg': 0,
            'percent_change': 0,
            'data': [dict(d) for d in data]
        })
    
    older_avg = sum(d['avg_ppm'] for d in older_data) / len(older_data)
    
    if older_avg == 0:
        trend = 'insufficient_data'
    else:
        percent_change = ((recent_avg - older_avg) / older_avg) * 100
        if percent_change > 5:
            trend = 'rising'
        elif percent_change < -5:
            trend = 'falling'
        else:
            trend = 'stable'
    
    return jsonify({
        'trend': trend,
        'recent_avg': round(recent_avg, 1),
        'older_avg': round(older_avg, 1),
        'percent_change': round(((recent_avg - older_avg) / older_avg) * 100, 1) if older_avg else 0,
        'data': [dict(d) for d in data]
    })


@analytics_bp.route('/custom', methods=['GET'])
@login_required
def analytics_custom_range():
    """Get data for custom date range"""
    end_date = request.args.get('end', date.today().isoformat())
    start_date = request.args.get('start', (date.today() - timedelta(days=30)).isoformat())
    
    db_source = resolve_source_param(allow_sim=True, allow_import=True)
    source_clause, source_params = build_source_filter(db_source)
    
    db = get_db()
    
    readings = db.execute(f"""
        SELECT timestamp, ppm FROM co2_readings
        WHERE DATE(timestamp) >= ? AND DATE(timestamp) <= ?
        AND {source_clause}
        ORDER BY timestamp
    """, (start_date, end_date, *source_params)).fetchall()
    
    stats = db.execute(f"""
        SELECT 
            COUNT(*) as count,
            AVG(ppm) as avg,
            MIN(ppm) as min,
            MAX(ppm) as max
        FROM co2_readings
        WHERE DATE(timestamp) >= ? AND DATE(timestamp) <= ?
        AND {source_clause}
    """, (start_date, end_date, *source_params)).fetchone()
    
    db.close()
    
    return jsonify({
        'readings': [dict(r) for r in readings],
        'stats': dict(stats) if stats else {'count': 0, 'avg': 0, 'min': 0, 'max': 0}
    })


@analytics_bp.route('/compare-periods', methods=['GET'])
@login_required
def compare_periods():
    """Compare CO₂ data between two time periods"""
    period_type = request.args.get('type', 'week')
    db_source = resolve_source_param(allow_sim=True, allow_import=True)
    source_clause, source_params = build_source_filter(db_source)
    
    db = get_db()
    
    if period_type == 'week':
        if db_source == 'import':
            date_range = db.execute(f"""
                SELECT MIN(timestamp) as min_date, MAX(timestamp) as max_date
                FROM co2_readings WHERE {source_clause}
            """, source_params).fetchone()
            
            if date_range and date_range['min_date'] and date_range['max_date']:
                current_data = db.execute(f"""
                    SELECT AVG(ppm) as avg, MIN(ppm) as min, MAX(ppm) as max, COUNT(*) as count
                    FROM co2_readings
                    WHERE {source_clause} AND timestamp >= (SELECT datetime((julianday(MIN(timestamp)) + julianday(MAX(timestamp))) / 2) FROM co2_readings WHERE {source_clause})
                """, (*source_params, *source_params)).fetchone()
                
                previous_data = db.execute(f"""
                    SELECT AVG(ppm) as avg, MIN(ppm) as min, MAX(ppm) as max, COUNT(*) as count
                    FROM co2_readings
                    WHERE {source_clause} AND timestamp < (SELECT datetime((julianday(MIN(timestamp)) + julianday(MAX(timestamp))) / 2) FROM co2_readings WHERE {source_clause})
                """, (*source_params, *source_params)).fetchone()
            else:
                current_data = {'avg': 0, 'min': 0, 'max': 0, 'count': 0}
                previous_data = {'avg': 0, 'min': 0, 'max': 0, 'count': 0}
        else:
            current_data = db.execute(f"""
                SELECT AVG(ppm) as avg, MIN(ppm) as min, MAX(ppm) as max, COUNT(*) as count
                FROM co2_readings
                WHERE timestamp >= datetime('now', '-7 days')
                AND {source_clause}
            """, source_params).fetchone()
            
            previous_data = db.execute(f"""
                SELECT AVG(ppm) as avg, MIN(ppm) as min, MAX(ppm) as max, COUNT(*) as count
                FROM co2_readings
                WHERE timestamp >= datetime('now', '-14 days') AND timestamp < datetime('now', '-7 days')
                AND {source_clause}
            """, source_params).fetchone()
    
    elif period_type == 'month':
        current_data = db.execute(f"""
            SELECT AVG(ppm) as avg, MIN(ppm) as min, MAX(ppm) as max, COUNT(*) as count
            FROM co2_readings
            WHERE timestamp >= datetime('now', 'start of month')
            AND {source_clause}
        """, source_params).fetchone()
        
        previous_data = db.execute(f"""
            SELECT AVG(ppm) as avg, MIN(ppm) as min, MAX(ppm) as max, COUNT(*) as count
            FROM co2_readings
            WHERE timestamp >= datetime('now', '-1 month', 'start of month')
            AND timestamp < datetime('now', 'start of month')
            AND {source_clause}
        """, source_params).fetchone()
    else:
        db.close()
        return jsonify({'error': 'Invalid period_type'}), 400
    
    db.close()
    
    def calc_diff(current, previous, field):
        if previous[field] is None or previous[field] == 0:
            return 0
        return round(((current[field] - previous[field]) / previous[field]) * 100, 1)
    
    return jsonify({
        'period': period_type,
        'current': dict(current_data) if current_data else {},
        'previous': dict(previous_data) if previous_data else {},
        'differences': {
            'avg_percent': calc_diff(current_data, previous_data, 'avg'),
            'min_percent': calc_diff(current_data, previous_data, 'min'),
            'max_percent': calc_diff(current_data, previous_data, 'max'),
        }
    })


@analytics_bp.route('/daily-comparison', methods=['GET'])
@login_required
def daily_comparison():
    """Get daily averages for trend visualization"""
    db_source = resolve_source_param(allow_sim=True, allow_import=True)
    source_clause, source_params = build_source_filter(db_source)
    
    db = get_db()
    
    if db_source == 'import':
        days_data = db.execute(f"""
            SELECT 
                DATE(timestamp) as date,
                AVG(ppm) as avg_ppm,
                MIN(ppm) as min_ppm,
                MAX(ppm) as max_ppm,
                COUNT(*) as readings
            FROM co2_readings
            WHERE {source_clause}
            GROUP BY DATE(timestamp)
            ORDER BY date ASC
        """, source_params).fetchall()
    else:
        days_data = db.execute(f"""
            SELECT 
                DATE(timestamp) as date,
                AVG(ppm) as avg_ppm,
                MIN(ppm) as min_ppm,
                MAX(ppm) as max_ppm,
                COUNT(*) as readings
            FROM co2_readings
            WHERE timestamp >= datetime('now', '-30 days')
            AND {source_clause}
            GROUP BY DATE(timestamp)
            ORDER BY date ASC
        """, source_params).fetchall()
    
    db.close()
    
    return jsonify({
        'days': 30,
        'data': [dict(d) for d in days_data]
    })


@analytics_bp.route('/report/pdf', methods=['GET'])
@login_required
def generate_pdf_report():
    """Generate PDF report with charts"""
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if not start_date or not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    db_source = resolve_source_param(allow_sim=False, allow_import=True)
    source_clause, source_params = build_source_filter(db_source)
    
    db = get_db()
    
    readings = db.execute(f"""
        SELECT DATE(timestamp) as date, AVG(ppm) as avg_ppm, MAX(ppm) as max_ppm, MIN(ppm) as min_ppm
        FROM co2_readings
        WHERE DATE(timestamp) >= ? AND DATE(timestamp) <= ?
        AND {source_clause}
        GROUP BY DATE(timestamp)
        ORDER BY date
    """, (start_date, end_date, *source_params)).fetchall()
    
    stats = db.execute(f"""
        SELECT 
            COUNT(*) as count,
            AVG(ppm) as avg,
            MIN(ppm) as min,
            MAX(ppm) as max
        FROM co2_readings
        WHERE DATE(timestamp) >= ? AND DATE(timestamp) <= ?
        AND {source_clause}
    """, (start_date, end_date, *source_params)).fetchone()
    
    db.close()
    
    # Build HTML for PDF
    html_content = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #3dd98f; }}
                .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }}
                .stat {{ padding: 15px; background: #f0f0f0; border-radius: 8px; text-align: center; }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #3dd98f; }}
                .stat-label {{ color: #666; margin-top: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #3dd98f; color: white; }}
            </style>
        </head>
        <body>
            <h1>🌬️ CO₂ Monitoring Report</h1>
            <p>Period: {start_date} to {end_date}</p>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{stats['count']}</div>
                    <div class="stat-label">Readings</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{round(stats['avg'], 1)}</div>
                    <div class="stat-label">Avg PPM</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{round(stats['min'], 0)}</div>
                    <div class="stat-label">Min PPM</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{round(stats['max'], 0)}</div>
                    <div class="stat-label">Max PPM</div>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Average PPM</th>
                        <th>Min PPM</th>
                        <th>Max PPM</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for row in readings:
        html_content += f"""
                    <tr>
                        <td>{row['date']}</td>
                        <td>{round(row['avg_ppm'], 1)}</td>
                        <td>{round(row['min_ppm'], 0)}</td>
                        <td>{round(row['max_ppm'], 0)}</td>
                    </tr>
        """
    
    html_content += """
                </tbody>
            </table>
        </body>
    </html>
    """
    
    try:
        from weasyprint import HTML
        pdf = HTML(string=html_content).write_pdf()
        from flask import make_response
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
        return response
    except Exception as e:
        return jsonify({'error': 'PDF generation failed', 'details': str(e)}), 500
