# fake_co2.py
import random
from database import get_db

# Global state for realistic mode
_current_value = 600  # Starting value
_trend = 0  # Current trend (-1: decreasing, 0: stable, 1: increasing)
_trend_counter = 0  # How long current trend has lasted

def generate_co2(realistic=True):
    global _current_value, _trend, _trend_counter
    
    if realistic:
        # Change trend every 5-15 readings
        _trend_counter += 1
        if _trend_counter > random.randint(5, 15):
            _trend = random.choice([-1, 0, 1])
            _trend_counter = 0
        
        # Apply trend with some randomness
        if _trend == 1:  # Increasing
            drift = random.uniform(5, 15)
        elif _trend == -1:  # Decreasing
            drift = random.uniform(-15, -5)
        else:  # Stable
            drift = random.uniform(-5, 5)
        
        _current_value += drift
        
        # Keep in realistic bounds
        _current_value = max(400, min(2000, _current_value))
        
        return int(_current_value)
    else:
        # Random mode
        return random.randint(400, 2000)

def save_reading(ppm: int):
    db = get_db()
    db.execute(
        "INSERT INTO co2_readings (ppm) VALUES (?)",
        (ppm,)
    )
    db.commit()
    db.close()

def reset_state(base_value=600):
    """Reset the CO2 generator state"""
    global _current_value, _trend, _trend_counter
    _current_value = base_value
    _trend = 0
    _trend_counter = 0
