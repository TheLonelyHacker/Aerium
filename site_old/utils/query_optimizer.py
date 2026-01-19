"""
Query Optimization Helper
Provides optimized query patterns and N+1 prevention
"""

from database import get_db
from typing import List, Dict, Any, Optional


class QueryOptimizer:
    """Provides optimized query patterns"""
    
    @staticmethod
    def get_dashboard_stats(user_id: int) -> Dict[str, Any]:
        """
        Get all dashboard statistics in optimized queries
        Replaces N+1 pattern with single optimized query set
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with all stats
        """
        db = get_db()
        cursor = db.cursor()
        
        try:
            # Get today's stats - single query
            today_stats = cursor.execute("""
                SELECT 
                    COUNT(*) as total_readings, 
                    AVG(ppm) as avg_ppm, 
                    MAX(ppm) as max_ppm, 
                    MIN(ppm) as min_ppm
                FROM co2_readings
                WHERE DATE(timestamp) = CURRENT_DATE
                    AND source IN ('live', 'simulator')
            """).fetchone()
            
            # Get week stats - single query
            week_stats = cursor.execute("""
                SELECT 
                    COUNT(*) as total_readings, 
                    AVG(ppm) as avg_ppm,
                    MIN(ppm) as min_ppm,
                    MAX(ppm) as max_ppm
                FROM co2_readings
                WHERE DATE(timestamp) >= DATE('now', '-7 days')
                    AND source IN ('live', 'simulator')
            """).fetchone()
            
            # Get user threshold and bad events - combined query
            user_threshold_data = cursor.execute("""
                SELECT 
                    COALESCE(ut.critical_level, 1200) as threshold,
                    (SELECT COUNT(*) FROM co2_readings 
                     WHERE DATE(timestamp) = CURRENT_DATE 
                     AND ppm > COALESCE(ut.critical_level, 1200)
                     AND source IN ('live', 'simulator')) as bad_events
                FROM user_thresholds ut
                WHERE ut.user_id = ?
            """, (user_id,)).fetchone()
            
            # Fallback if no threshold record
            if not user_threshold_data:
                bad_events_count = cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM co2_readings
                    WHERE DATE(timestamp) = CURRENT_DATE 
                        AND ppm > 1200
                        AND source IN ('live', 'simulator')
                """).fetchone()
                bad_events = bad_events_count['count'] if bad_events_count else 0
                user_threshold = 1200
            else:
                user_threshold = user_threshold_data['threshold']
                bad_events = user_threshold_data['bad_events']
            
            db.close()
            
            return {
                'today_stats': dict(today_stats) if today_stats else {'total_readings': 0, 'avg_ppm': 0},
                'week_stats': dict(week_stats) if week_stats else {'total_readings': 0, 'avg_ppm': 0},
                'bad_events': bad_events,
                'user_threshold': user_threshold
            }
        
        except Exception as e:
            db.close()
            raise e
    
    @staticmethod
    def get_sensor_readings_batch(sensor_ids: List[int], limit: int = 100) -> Dict[int, List[Dict]]:
        """
        Get readings for multiple sensors efficiently (prevents N+1)
        
        Args:
            sensor_ids: List of sensor IDs
            limit: Max readings per sensor
        
        Returns:
            Dictionary mapping sensor_id to readings list
        """
        if not sensor_ids:
            return {}
        
        db = get_db()
        cursor = db.cursor()
        
        try:
            placeholders = ', '.join(['?' for _ in sensor_ids])
            query = f"""
                SELECT 
                    sensor_id,
                    timestamp,
                    ppm,
                    temperature,
                    humidity
                FROM sensor_readings
                WHERE sensor_id IN ({placeholders})
                ORDER BY sensor_id, timestamp DESC
                LIMIT ?
            """
            
            readings = cursor.execute(query, (*sensor_ids, limit * len(sensor_ids))).fetchall()
            db.close()
            
            # Group by sensor ID
            result = {sensor_id: [] for sensor_id in sensor_ids}
            for reading in readings:
                sensor_id = reading['sensor_id']
                if sensor_id in result and len(result[sensor_id]) < limit:
                    result[sensor_id].append(dict(reading))
            
            return result
        
        except Exception as e:
            db.close()
            raise e
    
    @staticmethod
    def get_user_data_summary(user_id: int) -> Dict[str, Any]:
        """
        Get complete user data summary with optimized queries
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with user summary
        """
        db = get_db()
        cursor = db.cursor()
        
        try:
            # Single query to get user with settings and sensor count
            user_data = cursor.execute("""
                SELECT 
                    u.id,
                    u.username,
                    u.email,
                    u.email_verified,
                    u.role,
                    u.created_at,
                    COALESCE(us.co2_threshold, 800) as co2_threshold,
                    COALESCE(us.temperature_unit, 'C') as temperature_unit,
                    COALESCE(ut.critical_level, 1200) as critical_level,
                    (SELECT COUNT(*) FROM user_sensors WHERE user_id = u.id AND active = 1) as active_sensors,
                    (SELECT COUNT(*) FROM co2_readings WHERE source = 'live' AND timestamp >= datetime('now', '-24 hours')) as readings_24h
                FROM users u
                LEFT JOIN user_settings us ON u.id = us.user_id
                LEFT JOIN user_thresholds ut ON u.id = ut.user_id
                WHERE u.id = ?
            """, (user_id,)).fetchone()
            
            db.close()
            
            return dict(user_data) if user_data else {}
        
        except Exception as e:
            db.close()
            raise e
    
    @staticmethod
    def get_team_members_with_details(team_id: int) -> List[Dict]:
        """
        Get all team members with their details in one query
        
        Args:
            team_id: Team ID
        
        Returns:
            List of team member dictionaries
        """
        db = get_db()
        cursor = db.cursor()
        
        try:
            members = cursor.execute("""
                SELECT 
                    u.id,
                    u.username,
                    u.email,
                    u.role,
                    tm.role as team_role,
                    tm.joined_at,
                    (SELECT COUNT(*) FROM co2_readings WHERE source = 'live' AND timestamp >= datetime('now', '-7 days')) as readings_7d
                FROM team_members tm
                JOIN users u ON tm.user_id = u.id
                WHERE tm.team_id = ?
                ORDER BY tm.joined_at DESC
            """, (team_id,)).fetchall()
            
            db.close()
            
            return [dict(member) for member in members]
        
        except Exception as e:
            db.close()
            raise e
    
    @staticmethod
    def get_readings_with_stats(
        start_date: str,
        end_date: str,
        group_by: str = 'hour'
    ) -> List[Dict]:
        """
        Get readings grouped with statistics (prevents multiple queries)
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            group_by: 'hour', 'day', or 'week'
        
        Returns:
            List of grouped readings with stats
        """
        db = get_db()
        cursor = db.cursor()
        
        try:
            if group_by == 'day':
                group_expr = "strftime('%Y-%m-%d', timestamp)"
            elif group_by == 'week':
                group_expr = "strftime('%Y-W%W', timestamp)"
            else:  # hour
                group_expr = "strftime('%Y-%m-%d %H:00', timestamp)"
            
            query = f"""
                SELECT 
                    {group_expr} as period,
                    COUNT(*) as reading_count,
                    AVG(ppm) as avg_ppm,
                    MIN(ppm) as min_ppm,
                    MAX(ppm) as max_ppm,
                    STDDEV(ppm) as stddev_ppm,
                    (SELECT COUNT(*) FROM co2_readings r2 
                     WHERE DATE(r2.timestamp) = DATE(r1.timestamp) 
                     AND r2.ppm > 1200) as critical_readings
                FROM co2_readings r1
                WHERE DATE(timestamp) >= ? AND DATE(timestamp) <= ?
                    AND source IN ('live', 'simulator')
                GROUP BY {group_expr}
                ORDER BY period DESC
            """
            
            results = cursor.execute(query, (start_date, end_date)).fetchall()
            db.close()
            
            return [dict(row) for row in results]
        
        except Exception as e:
            db.close()
            raise e
