import sqlite3
from pathlib import Path

DB_PATH = Path("data/aerium.sqlite")

def get_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    cur = db.cursor()

    # CO₂ history
    cur.execute("""
        CREATE TABLE IF NOT EXISTS co2_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ppm INTEGER NOT NULL
        )
    """)
    
    # Create index on timestamp for faster queries
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_co2_timestamp 
        ON co2_readings(timestamp DESC)
    """)
    
    # Create index on date for daily queries
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_co2_date 
        ON co2_readings(date(timestamp))
    """)

    # Settings persistence
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    db.commit()
    db.close()

def cleanup_old_data(days_to_keep=90):
    """Remove CO₂ readings older than specified days (default 90 days)"""
    db = get_db()
    cur = db.cursor()
    
    cur.execute("""
        DELETE FROM co2_readings 
        WHERE timestamp < datetime('now', '-' || ? || ' days')
    """, (days_to_keep,))
    
    deleted_count = cur.rowcount
    db.commit()
    db.close()
    
    return deleted_count
