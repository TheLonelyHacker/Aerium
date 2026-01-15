import os
import time
from flask import Blueprint, jsonify, request, session
from utils.auth_decorators import login_required
from database import (
    create_sensor,
    get_user_sensors,
    get_sensor_by_id,
    update_sensor,
    delete_sensor,
    log_audit,
    get_sensor_readings,
    get_sensor_latest_reading,
    update_sensor_thresholds,
    get_sensor_thresholds,
)


sensors_bp = Blueprint("sensors", __name__, url_prefix="/api")

_sensor_mode = os.getenv("USE_SCD30", "1")
_sensor_last_read = 0


def _safe_audit(user_id, action, entity_type, entity_id, field, value, ip_address):
    try:
        log_audit(user_id, action, entity_type, entity_id, field, value, ip_address)
    except Exception:
        pass


@sensors_bp.route("/sensor/status")
@login_required
def sensor_status():
    """Get current sensor mode and availability status"""
    global _sensor_mode, _sensor_last_read

    try:
        from app.sensors.scd30 import SCD30

        scd30 = SCD30()
        try:
            reading = scd30.read()
            available = reading is not None
            _sensor_last_read = time.time()
        except Exception:
            available = False
    except Exception:
        available = False

    mode = "real" if _sensor_mode != "0" and available else "simulation"

    return jsonify(
        {
            "mode": mode,
            "available": available,
            "last_read": _sensor_last_read,
            "driver": "SCD30" if available else "None",
        }
    )


@sensors_bp.route("/sensor/mode", methods=["POST"])
@login_required
def set_sensor_mode():
    """Set sensor mode (real or simulation)"""
    global _sensor_mode

    data = request.get_json() or {}
    mode = data.get("mode", "simulation")

    if mode not in ["real", "simulation"]:
        return jsonify({"error": 'Invalid mode. Must be "real" or "simulation"'}), 400

    _sensor_mode = "1" if mode == "real" else "0"
    os.environ["USE_SCD30"] = _sensor_mode

    _safe_audit(session.get("user_id"), "SENSOR_MODE_CHANGE", "sensor", 0, "new_mode", mode, request.remote_addr)

    return jsonify({"success": True, "mode": mode, "message": f"Mode capteur défini à: {mode}"})


@sensors_bp.route("/sensor/test", methods=["POST"])
@login_required
def test_sensor():
    """Test SCD30 sensor connection"""
    data = request.get_json() or {}
    bus = int(data.get("bus", 1))
    address = data.get("address", "0x61")

    if isinstance(address, str):
        address = int(address, 16)

    try:
        from app.sensors.scd30 import SCD30

        scd30 = SCD30(bus=bus, address=address)
        reading = scd30.read()

        if reading and "co2" in reading:
            return jsonify(
                {
                    "success": True,
                    "co2": round(reading["co2"], 2),
                    "temperature": round(reading.get("temperature", 0), 2),
                    "humidity": round(reading.get("humidity", 0), 2),
                    "message": "Capteur détecté avec succès",
                }
            )
        return jsonify({"success": False, "error": "Capteur détecté mais pas de lecture disponible"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Impossible de se connecter au capteur: {str(e)}"}), 400


@sensors_bp.route("/sensors", methods=["GET"])
@login_required
def get_sensors_list():
    """Get all sensors for current user"""
    user_id = session.get("user_id")
    sensors = get_user_sensors(user_id)
    return jsonify(sensors)


@sensors_bp.route("/sensors", methods=["POST"])
@login_required
def create_new_sensor():
    """Create a new sensor"""
    user_id = session.get("user_id")
    data = request.get_json() or {}

    name = data.get("name", "").strip()
    sensor_type = data.get("type", "scd30")
    interface = data.get("interface", "i2c")
    config = data.get("config", {})

    if not name:
        return jsonify({"error": "Sensor name is required"}), 400

    sensor_id = create_sensor(user_id, name, sensor_type, interface, config)
    if not sensor_id:
        return jsonify({"error": "Sensor name already exists for this user"}), 400

    _safe_audit(user_id, "SENSOR_CREATED", "sensor", sensor_id, None, f"{name} ({sensor_type})", request.remote_addr)
    sensor = get_sensor_by_id(sensor_id, user_id)
    return jsonify(sensor), 201


@sensors_bp.route("/sensors/<int:sensor_id>", methods=["PUT"])
@login_required
def update_sensor_config(sensor_id):
    """Update sensor configuration"""
    user_id = session.get("user_id")
    data = request.get_json() or {}

    sensor = get_sensor_by_id(sensor_id, user_id)
    if not sensor:
        return jsonify({"error": "Sensor not found or not accessible"}), 404

    update_sensor(
        sensor_id,
        user_id,
        name=data.get("name"),
        sensor_type=data.get("type"),
        interface=data.get("interface"),
        config=data.get("config"),
        active=data.get("active"),
    )

    _safe_audit(user_id, "SENSOR_UPDATED", "sensor", sensor_id, None, data.get("name") or sensor["name"], request.remote_addr)
    updated_sensor = get_sensor_by_id(sensor_id, user_id)
    return jsonify(updated_sensor)


@sensors_bp.route("/sensors/<int:sensor_id>", methods=["DELETE"])
@login_required
def delete_sensor_endpoint(sensor_id):
    """Delete a sensor"""
    user_id = session.get("user_id")
    sensor = get_sensor_by_id(sensor_id, user_id)
    if not sensor:
        return jsonify({"error": "Sensor not found or not accessible"}), 404

    delete_sensor(sensor_id, user_id)
    _safe_audit(user_id, "SENSOR_DELETED", "sensor", sensor_id, sensor["name"], None, request.remote_addr)
    return jsonify({"success": True, "message": "Sensor deleted"})


@sensors_bp.route("/sensors/test", methods=["POST"])
@login_required
def test_sensor_connection():
    """Test sensor connection with provided configuration"""
    data = request.get_json() or {}
    sensor_type = data.get("type", "scd30")
    interface = data.get("interface", "i2c")
    config = data.get("config", {})

    if sensor_type == "scd30" and interface == "i2c":
        try:
            from app.sensors.scd30 import SCD30

            bus = config.get("bus", 1)
            address = config.get("address", "0x61")
            if isinstance(address, str):
                address = int(address, 16)
            scd30 = SCD30(bus=int(bus), address=address)
            reading = scd30.read()
            if reading and "co2" in reading:
                return jsonify(
                    {
                        "success": True,
                        "co2": round(reading.get("co2", 0), 2),
                        "temperature": round(reading.get("temperature", 0), 2),
                        "humidity": round(reading.get("humidity", 0), 2),
                        "message": "Capteur détecté",
                    }
                )
            return jsonify({"success": False, "error": "Capteur trouvé mais pas de lecture"})
        except Exception as e:
            return jsonify({"success": False, "error": f"Erreur SCD30: {str(e)}"})

    if sensor_type == "mhz19":
        return jsonify({"success": False, "error": "MH-Z19 support en développement"})

    return jsonify({"success": False, "error": f"Type de capteur non supporté: {sensor_type}"})


@sensors_bp.route("/sensor/<int:sensor_id>/readings")
@login_required
def get_sensor_readings_endpoint(sensor_id):
    """Get readings for a specific sensor (last 24 hours)"""
    user_id = session.get("user_id")
    hours = request.args.get("hours", 24, type=int)

    sensor = get_sensor_by_id(sensor_id, user_id)
    if not sensor:
        return jsonify({"error": "Sensor not found"}), 404

    readings = get_sensor_readings(sensor_id, hours)
    latest = get_sensor_latest_reading(sensor_id)

    return jsonify({"sensor_id": sensor_id, "sensor_name": sensor["name"], "readings": readings, "latest": latest, "count": len(readings)})


@sensors_bp.route("/sensor/<int:sensor_id>/thresholds", methods=["GET"])
@login_required
def get_sensor_thresholds_endpoint(sensor_id):
    """Get thresholds for a specific sensor"""
    user_id = session.get("user_id")
    sensor = get_sensor_by_id(sensor_id, user_id)
    if not sensor:
        return jsonify({"error": "Sensor not found"}), 404

    thresholds = get_sensor_thresholds(sensor_id, user_id)
    if thresholds:
        return jsonify({"good": thresholds.get("good_threshold", 800), "warning": thresholds.get("warning_threshold", 1000), "critical": thresholds.get("critical_threshold", 1200)})
    return jsonify({"error": "Thresholds not found"}), 404


@sensors_bp.route("/sensor/<int:sensor_id>/thresholds", methods=["PUT"])
@login_required
def update_sensor_thresholds_endpoint(sensor_id):
    """Update thresholds for a specific sensor"""
    user_id = session.get("user_id")
    data = request.get_json() or {}

    sensor = get_sensor_by_id(sensor_id, user_id)
    if not sensor:
        return jsonify({"error": "Sensor not found"}), 404

    success = update_sensor_thresholds(
        sensor_id,
        user_id,
        good=data.get("good"),
        warning=data.get("warning"),
        critical=data.get("critical"),
    )

    if success:
        _safe_audit(
            user_id,
            "SENSOR_THRESHOLDS_UPDATED",
            "sensor",
            sensor_id,
            None,
            f"{sensor['name']}: {data.get('good')}/{data.get('warning')}/{data.get('critical')}",
            request.remote_addr,
        )
        return jsonify({"success": True, "message": "Thresholds updated"})

    return jsonify({"error": "Failed to update thresholds"}), 400
