"""
CSV Import Validator
Comprehensive validation for CSV data imports
"""

import csv
import io
from datetime import datetime
from typing import Dict, List, Tuple, Any
from utils.constants import MAX_IMPORT_ROWS


class CSVValidator:
    """Validates CSV files before import"""
    
    # Required columns for CO₂ readings
    REQUIRED_COLUMNS = {'timestamp', 'ppm'}
    OPTIONAL_COLUMNS = {'temperature', 'humidity', 'source'}
    
    # Data type validation
    COLUMN_TYPES = {
        'timestamp': 'datetime',
        'ppm': 'float',
        'temperature': 'float',
        'humidity': 'float',
        'source': 'string'
    }
    
    # Value ranges
    VALUE_RANGES = {
        'ppm': (0, 2000),
        'temperature': (-50, 100),
        'humidity': (0, 100)
    }
    
    def __init__(self):
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.valid_rows: List[Dict[str, Any]] = []
        self.row_count = 0
        self.valid_count = 0
    
    def validate_file(self, file_stream: io.IOBase, max_rows: int = MAX_IMPORT_ROWS) -> Tuple[bool, Dict]:
        """
        Validate entire CSV file
        
        Args:
            file_stream: File object (BytesIO or similar)
            max_rows: Maximum number of rows to process
        
        Returns:
            Tuple of (is_valid: bool, result: Dict with details)
        """
        self.errors = []
        self.warnings = []
        self.valid_rows = []
        self.row_count = 0
        self.valid_count = 0
        
        try:
            # Decode file
            text_stream = io.TextIOWrapper(file_stream, encoding='utf-8')
            reader = csv.DictReader(text_stream)
            
            # Validate headers
            if not reader.fieldnames:
                self.errors.append({
                    'type': 'EMPTY_FILE',
                    'message': 'CSV file is empty or has no headers'
                })
                return False, self._get_result()
            
            header_validation = self._validate_headers(reader.fieldnames)
            if not header_validation['valid']:
                self.errors.extend(header_validation['errors'])
                return False, self._get_result()
            
            if header_validation['warnings']:
                self.warnings.extend(header_validation['warnings'])
            
            # Validate rows
            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                self.row_count += 1
                
                if self.row_count > max_rows:
                    self.warnings.append({
                        'type': 'MAX_ROWS_EXCEEDED',
                        'message': f'File has more than {max_rows} rows. Only first {max_rows} will be processed.',
                        'row': row_num
                    })
                    break
                
                # Skip empty rows
                if not any(row.values()):
                    continue
                
                row_validation = self._validate_row(row, row_num)
                if row_validation['valid']:
                    self.valid_rows.append(row_validation['data'])
                    self.valid_count += 1
                else:
                    self.errors.extend(row_validation['errors'])
        
        except UnicodeDecodeError:
            self.errors.append({
                'type': 'ENCODING_ERROR',
                'message': 'File encoding error. Please ensure CSV is UTF-8 encoded.'
            })
            return False, self._get_result()
        
        except Exception as e:
            self.errors.append({
                'type': 'PARSE_ERROR',
                'message': f'Error parsing CSV: {str(e)}'
            })
            return False, self._get_result()
        
        # Validation complete
        is_valid = len(self.errors) == 0 and self.valid_count > 0
        return is_valid, self._get_result()
    
    def _validate_headers(self, headers: List[str]) -> Dict:
        """Validate CSV headers"""
        headers_set = {h.strip().lower() for h in headers if h}
        result = {'valid': True, 'errors': [], 'warnings': []}
        
        # Check for required columns
        missing = self.REQUIRED_COLUMNS - headers_set
        if missing:
            result['valid'] = False
            result['errors'].append({
                'type': 'MISSING_COLUMNS',
                'message': f'Missing required columns: {", ".join(missing)}'
            })
        
        # Check for unknown columns
        all_valid = self.REQUIRED_COLUMNS | self.OPTIONAL_COLUMNS
        unknown = headers_set - all_valid
        if unknown:
            result['warnings'].append({
                'type': 'UNKNOWN_COLUMNS',
                'message': f'Unknown columns will be ignored: {", ".join(unknown)}'
            })
        
        return result
    
    def _validate_row(self, row: Dict[str, str], row_num: int) -> Dict:
        """Validate single row"""
        result = {'valid': True, 'data': {}, 'errors': []}
        
        try:
            # Validate required fields
            timestamp_str = row.get('timestamp', '').strip()
            ppm_str = row.get('ppm', '').strip()
            
            if not timestamp_str:
                result['valid'] = False
                result['errors'].append({
                    'type': 'MISSING_TIMESTAMP',
                    'row': row_num,
                    'message': 'Missing timestamp value'
                })
                return result
            
            if not ppm_str:
                result['valid'] = False
                result['errors'].append({
                    'type': 'MISSING_PPM',
                    'row': row_num,
                    'message': 'Missing ppm value'
                })
                return result
            
            # Parse and validate timestamp
            try:
                # Try multiple datetime formats
                timestamp = None
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']:
                    try:
                        timestamp = datetime.strptime(timestamp_str, fmt)
                        break
                    except ValueError:
                        continue
                
                if timestamp is None:
                    result['valid'] = False
                    result['errors'].append({
                        'type': 'INVALID_TIMESTAMP_FORMAT',
                        'row': row_num,
                        'message': f'Invalid timestamp format: {timestamp_str}. Use YYYY-MM-DD HH:MM:SS',
                        'value': timestamp_str
                    })
                    return result
                
                result['data']['timestamp'] = timestamp.isoformat()
            
            except Exception as e:
                result['valid'] = False
                result['errors'].append({
                    'type': 'TIMESTAMP_PARSE_ERROR',
                    'row': row_num,
                    'message': f'Error parsing timestamp: {str(e)}'
                })
                return result
            
            # Parse and validate PPM
            try:
                ppm = float(ppm_str)
                
                min_ppm, max_ppm = self.VALUE_RANGES['ppm']
                if not (min_ppm <= ppm <= max_ppm):
                    result['valid'] = False
                    result['errors'].append({
                        'type': 'PPM_OUT_OF_RANGE',
                        'row': row_num,
                        'message': f'PPM value {ppm} out of valid range ({min_ppm}-{max_ppm})',
                        'value': ppm
                    })
                    return result
                
                result['data']['ppm'] = ppm
            
            except ValueError:
                result['valid'] = False
                result['errors'].append({
                    'type': 'INVALID_PPM_FORMAT',
                    'row': row_num,
                    'message': f'PPM must be a number, got: {ppm_str}',
                    'value': ppm_str
                })
                return result
            
            # Optional: temperature
            if row.get('temperature', '').strip():
                try:
                    temp = float(row['temperature'].strip())
                    min_temp, max_temp = self.VALUE_RANGES['temperature']
                    if not (min_temp <= temp <= max_temp):
                        result['errors'].append({
                            'type': 'TEMPERATURE_OUT_OF_RANGE',
                            'row': row_num,
                            'message': f'Temperature {temp}°C out of valid range ({min_temp}-{max_temp}°C)',
                            'value': temp
                        })
                    else:
                        result['data']['temperature'] = temp
                except ValueError:
                    result['errors'].append({
                        'type': 'INVALID_TEMPERATURE_FORMAT',
                        'row': row_num,
                        'message': f'Temperature must be a number, got: {row["temperature"]}'
                    })
            
            # Optional: humidity
            if row.get('humidity', '').strip():
                try:
                    humidity = float(row['humidity'].strip())
                    min_hum, max_hum = self.VALUE_RANGES['humidity']
                    if not (min_hum <= humidity <= max_hum):
                        result['errors'].append({
                            'type': 'HUMIDITY_OUT_OF_RANGE',
                            'row': row_num,
                            'message': f'Humidity {humidity}% out of valid range ({min_hum}-{max_hum}%)',
                            'value': humidity
                        })
                    else:
                        result['data']['humidity'] = humidity
                except ValueError:
                    result['errors'].append({
                        'type': 'INVALID_HUMIDITY_FORMAT',
                        'row': row_num,
                        'message': f'Humidity must be a number, got: {row["humidity"]}'
                    })
            
            # Set source to 'import'
            result['data']['source'] = 'import'
            
            # If there are errors but data is partially valid, mark as invalid
            if result['errors']:
                result['valid'] = False
        
        except Exception as e:
            result['valid'] = False
            result['errors'].append({
                'type': 'ROW_VALIDATION_ERROR',
                'row': row_num,
                'message': f'Error validating row: {str(e)}'
            })
        
        return result
    
    def _get_result(self) -> Dict:
        """Build result dictionary"""
        return {
            'total_rows': self.row_count,
            'valid_rows': self.valid_count,
            'invalid_rows': self.row_count - self.valid_count,
            'errors': self.errors,
            'warnings': self.warnings,
            'data': self.valid_rows
        }
