'''
Fichier pour tester l'app sans capteur de co2
'''
import random
import time
import os

def fake_read_co2():
    """
    Simule une valeur de CO₂ entre 400 et 2000 ppm.
    """
    return random.randint(400, 2000)


def get_air_quality(ppm):
    """
    Retourne une classification de la qualité de l'air en fonction du ppm.
    """
    if ppm < 800:
        return "Bon"
    elif ppm < 1200:
        return "Moyen"
    else:
        return "Mauvais"


def alert_needed(ppm, threshold=1200):
    """
    Retourne True si le ppm dépasse le seuil d'alerte défini.
    Par défaut : 1200 ppm.
    """
    return ppm > threshold


if __name__ == "__main__":
    import time
    # Try to use an attached SCD30 sensor when available. Set environment
    # variable USE_SCD30=0 to force the fake reader.
    try:
        from app.sensors.scd30 import SCD30
        _scd30 = SCD30()
    except Exception:
        _scd30 = None

    use_scd = os.environ.get("USE_SCD30", "1")
    while True:
        ppm = None
        extra = ""
        if use_scd != "0" and _scd30 is not None:
            try:
                reading = _scd30.read()
                if reading and "co2" in reading:
                    ppm = int(reading["co2"])
                    extra = f" | T: {reading.get('temperature')}°C | RH: {reading.get('humidity')}%"
            except Exception:
                ppm = None

        if ppm is None:
            ppm = fake_read_co2()

        quality = get_air_quality(ppm)
        alert = alert_needed(ppm)

        print(f"CO₂ : {ppm} ppm | Qualité : {quality} | Alerte : {alert}{extra}")
        time.sleep(1)
