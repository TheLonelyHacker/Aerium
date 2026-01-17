"""
Data Export Blueprint
Provides data export functionality via CSV, Excel, and PDF
"""
from flask import Blueprint, request, jsonify, send_file, render_template
from utils.auth_decorators import login_required
from utils.logger import configure_logging
from database import get_db
from datetime import datetime, timedelta
import io

# Import DataExporter carefully to handle weasyprint issues on Windows
try:
    from utils.export_manager import DataExporter
except (ImportError, OSError) as e:
    # If import fails due to weasyprint issues, create a minimal version
    class DataExporter:
        OPENPYXL_AVAILABLE = False
        WEASYPRINT_AVAILABLE = False
        
        def export_to_csv(self, data, filename="export"):
            import csv
            output = io.StringIO()
            if not data:
                return io.BytesIO()
            fieldnames = data[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            output.seek(0)
            return io.BytesIO(output.getvalue().encode('utf-8'))
        
        def export_to_excel(self, data, title="Report"):
            return None
        
        def export_to_pdf(self, data, title="Report"):
            return None

logger = configure_logging()
export_bp = Blueprint('export', __name__, url_prefix='/export')


def initialize_export_tables():
    """Initialize export-related database tables"""
    # Tables already initialized in database.py init_db()
    pass


@export_bp.route('/')
@login_required
def index():
    """Export page"""
    return render_template('data-export/export-manager.html')


@export_bp.route('/api/export', methods=['POST'])
@login_required
def export_data():
    """Export CO₂ data in requested format"""
    data = request.get_json() or {}
    
    format_type = data.get('format', 'csv').lower()
    days_back = int(data.get('days_back', 7))
    
    if format_type not in ['csv', 'excel', 'pdf']:
        return jsonify({'error': 'Invalid format. Must be csv, excel, or pdf'}), 400
    
    if days_back < 1 or days_back > 365:
        return jsonify({'error': 'days_back must be between 1 and 365'}), 400
    
    try:
        # Get data from database
        db = get_db()
        start_date = datetime.now() - timedelta(days=days_back)
        
        readings = db.execute("""
            SELECT timestamp, ppm, temperature, humidity, source
            FROM co2_readings
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """, (start_date,)).fetchall()
        
        db.close()
        
        if not readings:
            return jsonify({'error': 'No data available for selected period'}), 404
        
        # Convert to list of dicts
        data_list = [
            {
                'timestamp': r['timestamp'],
                'ppm': r['ppm'],
                'temperature': r['temperature'],
                'humidity': r['humidity'],
                'source': r['source']
            } 
            for r in readings
        ]
        
        exporter = DataExporter()
        filename = f"aerium_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if format_type == 'csv':
            output = exporter.export_to_csv(data_list, filename)
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f"{filename}.csv"
            )
        elif format_type == 'excel':
            output = exporter.export_to_excel(data_list, title='Aerium CO₂ Report')
            if output is None:
                logger.warning("Excel export attempted but openpyxl not available")
                return jsonify({'error': 'Excel export not available (openpyxl not installed)'}), 501
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f"{filename}.xlsx"
            )
        elif format_type == 'pdf':
            output = exporter.export_to_pdf(data_list, title='Aerium CO₂ Report')
            if output is None:
                logger.warning("PDF export attempted but WeasyPrint not available")
                return jsonify({
                    'error': 'PDF export not available on this system (WeasyPrint requires GTK support)',
                    'alternatives': ['csv', 'excel']
                }), 501
            return send_file(
                output,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"{filename}.pdf"
            )
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500


@export_bp.route('/api/formats', methods=['GET'])
@login_required
def get_available_formats():
    """Get available export formats based on installed dependencies"""
    exporter = DataExporter()
    
    formats = {
        'csv': {'available': True, 'description': 'Comma-separated values'},
        'excel': {
            'available': exporter.openpyxl_available,
            'description': 'Microsoft Excel workbook'
        },
        'pdf': {
            'available': exporter.weasyprint_available,
            'description': 'Portable Document Format',
            'note': 'Not available on Windows without additional GTK dependencies'
        }
    }
    
    return jsonify(formats)
