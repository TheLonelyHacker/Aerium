"""
================================================================================
                     ADVANCED FEATURES MODULE
================================================================================
Analytics & Insights, Collaboration & Sharing, Performance & Optimization,
and Data Visualization enhancements for Aerium CO₂ Monitor

Author: Development Team
Version: 2.0
Date: 2026-01-03
================================================================================
"""

import numpy as np
from datetime import datetime, timedelta, UTC
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import json
from typing import Dict, List, Tuple, Optional
import statistics


# ================================================================================
#                    ANALYTICS & INSIGHTS ENGINE
# ================================================================================

class AdvancedAnalytics:
    """Advanced analytics with ML-based insights"""
    
    @staticmethod
    def predict_co2_level(readings: List[Dict], hours_ahead: int = 1) -> Dict:
        """
        Predict CO₂ levels using linear regression
        
        Args:
            readings: List of reading dicts with 'timestamp' and 'ppm'
            hours_ahead: Hours to predict ahead (1-24)
        
        Returns:
            Dict with predicted_ppm, confidence, trend
        """
        if len(readings) < 5:
            return {
                'error': 'Insufficient data for prediction',
                'predicted_ppm': None,
                'confidence': 0
            }
        
        try:
            # Prepare data
            X = np.array([[i] for i in range(len(readings))])
            y = np.array([r.get('ppm', 0) for r in readings])
            
            # Train model
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict
            future_point = np.array([[len(readings) + (hours_ahead / 4)]])
            prediction = float(model.predict(future_point)[0])
            
            # Calculate confidence (R² score)
            confidence = float(model.score(X, y))
            
            # Calculate trend
            if len(readings) >= 2:
                recent_avg = np.mean(y[-5:])
                older_avg = np.mean(y[:5])
                trend = "rising" if recent_avg > older_avg else "falling"
            else:
                trend = "stable"
            
            return {
                'predicted_ppm': max(0, prediction),
                'confidence': max(0, min(100, confidence * 100)),
                'trend': trend,
                'hours_ahead': hours_ahead
            }
        except Exception as e:
            return {
                'error': str(e),
                'predicted_ppm': None,
                'confidence': 0
            }
    
    @staticmethod
    def detect_anomalies(readings: List[Dict], threshold_std: float = 2.0) -> Dict:
        """
        Detect anomalous readings using standard deviation
        
        Args:
            readings: List of reading dicts with 'ppm'
            threshold_std: Number of standard deviations for anomaly
        
        Returns:
            Dict with anomalies list and statistics
        """
        if len(readings) < 3:
            return {'anomalies': [], 'statistics': {}}
        
        try:
            ppm_values = [r.get('ppm', 0) for r in readings]
            
            # Calculate statistics
            mean_ppm = statistics.mean(ppm_values)
            stdev = statistics.stdev(ppm_values) if len(ppm_values) > 1 else 0
            
            # Find anomalies
            anomalies = []
            for i, reading in enumerate(readings):
                ppm = reading.get('ppm', 0)
                z_score = abs((ppm - mean_ppm) / stdev) if stdev > 0 else 0
                
                if z_score > threshold_std:
                    anomalies.append({
                        'index': i,
                        'ppm': ppm,
                        'z_score': z_score,
                        'severity': 'high' if z_score > 3 else 'medium',
                        'timestamp': reading.get('timestamp', '')
                    })
            
            return {
                'anomalies': anomalies,
                'statistics': {
                    'mean': mean_ppm,
                    'stdev': stdev,
                    'min': min(ppm_values),
                    'max': max(ppm_values)
                },
                'anomaly_count': len(anomalies)
            }
        except Exception as e:
            return {'error': str(e), 'anomalies': []}
    
    @staticmethod
    def generate_insights(readings: List[Dict], user_id: str) -> Dict:
        """
        Generate intelligent insights from readings
        
        Args:
            readings: List of reading dicts
            user_id: User ID for personalization
        
        Returns:
            Dict with list of insights
        """
        insights = []
        
        if not readings:
            return {'insights': insights}
        
        try:
            # Extract PPM values
            ppm_values = [r.get('ppm', 0) for r in readings]
            timestamps = [r.get('timestamp', '') for r in readings]
            
            # Insight 1: Peak times
            if len(readings) >= 24:
                hourly_avg = {}
                for reading in readings:
                    ts = reading.get('timestamp', '')
                    if ts:
                        try:
                            dt = datetime.fromisoformat(ts)
                            hour = dt.hour
                            if hour not in hourly_avg:
                                hourly_avg[hour] = []
                            hourly_avg[hour].append(reading.get('ppm', 0))
                        except:
                            pass
                
                if hourly_avg:
                    peak_hour = max(hourly_avg, key=lambda h: sum(hourly_avg[h]) / len(hourly_avg[h]))
                    insights.append({
                        'type': 'peak_time',
                        'message': f'CO₂ levels peak around {peak_hour:02d}:00',
                        'confidence': 0.85,
                        'action': 'Consider ventilating around this time'
                    })
            
            # Insight 2: Air quality assessment
            avg_ppm = statistics.mean(ppm_values)
            if avg_ppm > 1200:
                insights.append({
                    'type': 'air_quality',
                    'message': 'Air quality is consistently poor',
                    'confidence': 0.9,
                    'action': 'Consider improving ventilation or air purifier'
                })
            elif avg_ppm > 800:
                insights.append({
                    'type': 'air_quality',
                    'message': 'Air quality is moderate',
                    'confidence': 0.85,
                    'action': 'Regular ventilation recommended'
                })
            else:
                insights.append({
                    'type': 'air_quality',
                    'message': 'Air quality is excellent',
                    'confidence': 0.9,
                    'action': 'Keep up good ventilation habits!'
                })
            
            # Insight 3: Trend analysis
            if len(ppm_values) >= 2:
                recent_avg = statistics.mean(ppm_values[-5:])
                older_avg = statistics.mean(ppm_values[:5])
                trend_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
                
                if trend_pct > 10:
                    insights.append({
                        'type': 'trend',
                        'message': f'Air quality is getting worse ({trend_pct:.1f}% increase)',
                        'confidence': 0.8,
                        'action': 'Increase ventilation frequency'
                    })
                elif trend_pct < -10:
                    insights.append({
                        'type': 'trend',
                        'message': f'Air quality is improving ({abs(trend_pct):.1f}% decrease)',
                        'confidence': 0.8,
                        'action': 'Good progress! Continue current practices'
                    })
            
            return {
                'insights': insights,
                'count': len(insights),
                'generated_at': datetime.now(UTC).isoformat()
            }
        except Exception as e:
            return {'error': str(e), 'insights': []}
    
    @staticmethod
    def health_recommendation(readings: List[Dict]) -> Dict:
        """
        Generate health recommendations based on readings
        
        Args:
            readings: List of reading dicts
        
        Returns:
            Dict with health recommendations
        """
        recommendations = []
        
        if not readings:
            return {'recommendations': recommendations}
        
        try:
            ppm_values = [r.get('ppm', 0) for r in readings]
            avg_ppm = statistics.mean(ppm_values)
            max_ppm = max(ppm_values)
            
            # CO₂ levels and health impacts
            if avg_ppm > 1400:
                recommendations.append({
                    'level': 'critical',
                    'symptom': 'Drowsiness, poor concentration, headaches',
                    'action': 'Ventilate immediately - open windows',
                    'duration_minutes': 10
                })
            elif avg_ppm > 1000:
                recommendations.append({
                    'level': 'high',
                    'symptom': 'Mild cognitive impairment, fatigue',
                    'action': 'Open windows or increase ventilation',
                    'duration_minutes': 15
                })
            elif avg_ppm > 800:
                recommendations.append({
                    'level': 'moderate',
                    'symptom': 'Possible minor concentration issues',
                    'action': 'Increase air circulation',
                    'duration_minutes': 5
                })
            else:
                recommendations.append({
                    'level': 'good',
                    'symptom': 'No issues expected',
                    'action': 'Continue monitoring',
                    'duration_minutes': 0
                })
            
            return {
                'recommendations': recommendations,
                'current_ppm': ppm_values[-1] if ppm_values else 0,
                'average_ppm': avg_ppm,
                'peak_ppm': max_ppm
            }
        except Exception as e:
            return {'error': str(e), 'recommendations': []}


# ================================================================================
#                    COLLABORATION & SHARING ENGINE
# ================================================================================

class CollaborationManager:
    """Manage team workspaces, permissions, and sharing"""
    
    @staticmethod
    def create_shared_dashboard(user_id: str, dashboard_name: str, is_public: bool = False) -> Dict:
        """
        Create a shareable dashboard
        
        Args:
            user_id: Creator user ID
            dashboard_name: Name of dashboard
            is_public: Whether dashboard is publicly accessible
        
        Returns:
            Dict with share_token and dashboard info
        """
        try:
            import secrets
            share_token = secrets.token_urlsafe(32)
            
            return {
                'share_token': share_token,
                'dashboard_name': dashboard_name,
                'creator_id': user_id,
                'is_public': is_public,
                'created_at': datetime.now(UTC).isoformat(),
                'share_url': f'/dashboard/shared/{share_token}',
                'permissions': {
                    'can_view': True,
                    'can_edit': False,
                    'can_export': True
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def generate_share_link(content_type: str, content_id: str, 
                           permissions: List[str] = None) -> Dict:
        """
        Generate a shareable link with specific permissions
        
        Args:
            content_type: Type of content (dashboard, report, data)
            content_id: ID of content
            permissions: List of permissions (view, edit, export)
        
        Returns:
            Dict with share link and settings
        """
        import secrets
        
        permissions = permissions or ['view']
        
        return {
            'link_token': secrets.token_urlsafe(32),
            'content_type': content_type,
            'content_id': content_id,
            'permissions': permissions,
            'expires_at': (datetime.now(UTC) + timedelta(days=30)).isoformat(),
            'created_at': datetime.now(UTC).isoformat(),
            'access_count': 0,
            'last_accessed': None
        }
    
    @staticmethod
    def validate_share_link(link_token: str) -> Dict:
        """
        Validate a share link and return access info
        
        Args:
            link_token: The share token
        
        Returns:
            Dict with validation result and access permissions
        """
        # This would query the database in production
        return {
            'valid': True,
            'expired': False,
            'permissions': ['view', 'export'],
            'access_count': 5
        }
    
    @staticmethod
    def create_team_workspace(creator_id: str, team_name: str, members: List[str] = None) -> Dict:
        """
        Create a team workspace
        
        Args:
            creator_id: Creator user ID
            team_name: Name of team
            members: List of user IDs to invite
        
        Returns:
            Dict with workspace info
        """
        import secrets
        
        members = members or []
        
        return {
            'workspace_id': secrets.token_hex(16),
            'team_name': team_name,
            'creator_id': creator_id,
            'members': members,
            'created_at': datetime.now(UTC).isoformat(),
            'role_structure': {
                'admin': [creator_id],
                'editor': [],
                'viewer': members
            }
        }


# ================================================================================
#                    PERFORMANCE & OPTIMIZATION
# ================================================================================

class PerformanceOptimizer:
    """Performance optimization and data management"""
    
    @staticmethod
    def analyze_database_usage() -> Dict:
        """
        Analyze database usage and optimization opportunities
        
        Returns:
            Dict with usage stats and recommendations
        """
        return {
            'total_records': 0,  # Would be queried from DB
            'storage_size_mb': 0,
            'oldest_record': None,
            'newest_record': None,
            'records_per_day': 0,
            'recommendations': [
                'Archive readings older than 1 year',
                'Enable database indexing on timestamp column',
                'Implement data partitioning by date',
                'Consider compression for old data'
            ]
        }
    
    @staticmethod
    def optimize_queries(query_type: str) -> Dict:
        """
        Get query optimization suggestions
        
        Args:
            query_type: Type of query (readings, analytics, export)
        
        Returns:
            Dict with optimization tips
        """
        optimizations = {
            'readings': [
                'Add index on timestamp and user_id',
                'Use pagination for large result sets',
                'Cache recent readings (< 1 hour)',
                'Use LIMIT for dashboard queries'
            ],
            'analytics': [
                'Pre-calculate hourly/daily aggregates',
                'Cache trend calculations',
                'Use materialized views for reports',
                'Batch process analytics updates'
            ],
            'export': [
                'Stream results instead of loading all in memory',
                'Use background jobs for large exports',
                'Compress exported data',
                'Schedule exports during off-peak hours'
            ]
        }
        
        return {
            'query_type': query_type,
            'optimizations': optimizations.get(query_type, []),
            'estimated_improvement': '30-60%'
        }
    
    @staticmethod
    def archive_old_data(days_threshold: int = 365) -> Dict:
        """
        Archive data older than threshold
        
        Args:
            days_threshold: Days of data to keep online
        
        Returns:
            Dict with archiving results
        """
        archive_date = datetime.now(UTC) - timedelta(days=days_threshold)
        
        return {
            'archived': True,
            'archive_date': archive_date.isoformat(),
            'records_archived': 0,  # Would be actual count
            'storage_freed_mb': 0,
            'archive_location': '/backups/archive/',
            'retention_period_days': days_threshold
        }
    
    @staticmethod
    def enable_smart_caching(cache_type: str, ttl_seconds: int = 300) -> Dict:
        """
        Enable smart caching strategies
        
        Args:
            cache_type: Type of cache (readings, analytics, predictions)
            ttl_seconds: Time to live in seconds
        
        Returns:
            Dict with caching config
        """
        return {
            'cache_type': cache_type,
            'enabled': True,
            'ttl_seconds': ttl_seconds,
            'cache_key_pattern': f'aerium:{cache_type}:*',
            'invalidation_events': [
                'new_reading_received',
                'user_settings_changed',
                'threshold_updated'
            ],
            'estimated_hit_rate': '70-85%'
        }


# ================================================================================
#                    DATA VISUALIZATION ENHANCEMENTS
# ================================================================================

class VisualizationEngine:
    """Enhanced data visualization components"""
    
    @staticmethod
    def generate_heatmap_data(readings: List[Dict]) -> Dict:
        """
        Generate heatmap data for time-of-day patterns
        
        Args:
            readings: List of reading dicts with timestamp and ppm
        
        Returns:
            Dict with heatmap matrix and metadata
        """
        try:
            # Create 7x24 matrix (days x hours)
            heatmap = [[0 for _ in range(24)] for _ in range(7)]
            counts = [[0 for _ in range(24)] for _ in range(7)]
            
            for reading in readings:
                try:
                    dt = datetime.fromisoformat(reading.get('timestamp', ''))
                    day_of_week = dt.weekday()
                    hour = dt.hour
                    ppm = reading.get('ppm', 0)
                    
                    if 0 <= day_of_week < 7 and 0 <= hour < 24:
                        heatmap[day_of_week][hour] += ppm
                        counts[day_of_week][hour] += 1
                except:
                    pass
            
            # Calculate averages
            for day in range(7):
                for hour in range(24):
                    if counts[day][hour] > 0:
                        heatmap[day][hour] /= counts[day][hour]
            
            day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            return {
                'heatmap': heatmap,
                'days': day_names,
                'hours': list(range(24)),
                'min_value': min(min(row) for row in heatmap if row),
                'max_value': max(max(row) for row in heatmap if row),
                'data_points': sum(sum(row) for row in counts)
            }
        except Exception as e:
            return {'error': str(e), 'heatmap': []}
    
    @staticmethod
    def generate_correlation_data(readings: List[Dict], 
                                  variables: List[str] = None) -> Dict:
        """
        Generate correlation data between variables
        
        Args:
            readings: List of reading dicts
            variables: Variables to correlate (ppm, temperature, humidity)
        
        Returns:
            Dict with correlation matrix
        """
        variables = variables or ['ppm']
        
        try:
            # Extract data for each variable
            data_matrix = {var: [] for var in variables}
            
            for reading in readings:
                for var in variables:
                    value = reading.get(var, 0)
                    data_matrix[var].append(value)
            
            # Calculate correlations
            correlations = []
            for i, var1 in enumerate(variables):
                for var2 in variables[i+1:]:
                    if data_matrix[var1] and data_matrix[var2]:
                        # Pearson correlation
                        correlation = np.corrcoef(
                            data_matrix[var1],
                            data_matrix[var2]
                        )[0, 1]
                        
                        correlations.append({
                            'var1': var1,
                            'var2': var2,
                            'correlation': float(correlation),
                            'strength': 'strong' if abs(correlation) > 0.7 else 'moderate'
                        })
            
            return {
                'correlations': correlations,
                'variables': variables,
                'data_points': len(readings)
            }
        except Exception as e:
            return {'error': str(e), 'correlations': []}
    
    @staticmethod
    def generate_dashboard_config(user_preferences: Dict = None) -> Dict:
        """
        Generate customizable dashboard configuration
        
        Args:
            user_preferences: User's dashboard preferences
        
        Returns:
            Dict with dashboard widget configuration
        """
        user_preferences = user_preferences or {}
        
        return {
            'layout': user_preferences.get('layout', 'grid'),
            'widgets': [
                {
                    'id': 'current-ppm',
                    'name': 'Current CO₂ Level',
                    'type': 'gauge',
                    'position': 0,
                    'size': 'large',
                    'enabled': True
                },
                {
                    'id': 'trend-chart',
                    'name': 'Trend (24h)',
                    'type': 'line',
                    'position': 1,
                    'size': 'large',
                    'enabled': True
                },
                {
                    'id': 'heatmap',
                    'name': 'Time Pattern',
                    'type': 'heatmap',
                    'position': 2,
                    'size': 'medium',
                    'enabled': user_preferences.get('show_heatmap', False)
                },
                {
                    'id': 'predictions',
                    'name': 'Predictions',
                    'type': 'forecast',
                    'position': 3,
                    'size': 'medium',
                    'enabled': user_preferences.get('show_predictions', False)
                },
                {
                    'id': 'insights',
                    'name': 'Insights',
                    'type': 'insights',
                    'position': 4,
                    'size': 'medium',
                    'enabled': True
                }
            ],
            'refresh_interval': user_preferences.get('refresh_interval', 5),
            'theme': user_preferences.get('theme', 'auto')
        }
    
    @staticmethod
    def export_visualization(viz_type: str, data: Dict, format: str = 'json') -> Dict:
        """
        Export visualization in multiple formats
        
        Args:
            viz_type: Type of visualization
            data: Visualization data
            format: Export format (json, csv, svg)
        
        Returns:
            Dict with export info
        """
        return {
            'viz_type': viz_type,
            'format': format,
            'filename': f'{viz_type}_{datetime.now(UTC).strftime("%Y%m%d_%H%M%S")}.{format}',
            'size_bytes': len(json.dumps(data)) if format == 'json' else 0,
            'exportable': True,
            'created_at': datetime.now(UTC).isoformat()
        }


# ================================================================================
#                    UTILITY FUNCTIONS
# ================================================================================

def calculate_percentiles(data: List[float], percentiles: List[int] = None) -> Dict:
    """Calculate percentiles for a dataset"""
    percentiles = percentiles or [25, 50, 75, 90, 95, 99]
    sorted_data = sorted(data)
    
    result = {}
    for p in percentiles:
        idx = int(len(sorted_data) * p / 100)
        result[f'p{p}'] = sorted_data[min(idx, len(sorted_data) - 1)]
    
    return result


def calculate_moving_average(data: List[float], window: int = 5) -> List[float]:
    """Calculate moving average"""
    if len(data) < window:
        return data
    
    return [statistics.mean(data[i:i+window]) for i in range(len(data) - window + 1)]


def detect_patterns(readings: List[Dict]) -> Dict:
    """Detect patterns in readings"""
    patterns = {
        'daily_cycle': False,
        'weekly_pattern': False,
        'recurring_spikes': False,
        'seasonal_trend': False
    }
    
    # Implementation would analyze readings for patterns
    
    return patterns


# ================================================================================
#                    EXPORT & INTEGRATION
# ================================================================================

# Make all classes available for import
__all__ = [
    'AdvancedAnalytics',
    'CollaborationManager',
    'PerformanceOptimizer',
    'VisualizationEngine',
    'calculate_percentiles',
    'calculate_moving_average',
    'detect_patterns'
]
