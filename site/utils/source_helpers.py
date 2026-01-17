"""Shared helpers for normalizing data sources.

Keeps source aliases consistent across HTTP and analytics code paths so live data
never mixes with simulator/imported data.
"""
from flask import request

# Centralized source aliases
REAL_SOURCES = ("live", "sensor", "real", "live_real")
SIM_SOURCES = ("sim",)
IMPORT_SOURCES = ("import",)


def resolve_source_param(*, default: str = "live", allow_sim: bool = False, allow_import: bool = False) -> str:
    """Normalize ?source= to one of: live, sim, import.

    Args:
        default: Fallback source when none provided or blocked.
        allow_sim: Whether simulator data is allowed for this endpoint.
        allow_import: Whether imported CSV data is allowed.
    """
    raw = (request.args.get("source") or default)
    normalized_map = {
        "live": "live",
        "real": "live",
        "hardware": "live",
        "sensor": "live",
        "live_real": "live",
        "simulation": "sim",
        "sim": "sim",
        "simulator": "sim",
        "import": "import",
        "csv": "import",
    }
    normalized = normalized_map.get(str(raw).lower(), "live")

    if normalized == "sim" and not allow_sim:
        normalized = "live"
    if normalized == "import" and not allow_import:
        normalized = "live"

    return normalized


def build_source_filter(db_source: str) -> tuple[str, tuple[str, ...]]:
    """Return SQL clause + params for the chosen data source bucket."""
    if db_source == "sim":
        return "source = ?", SIM_SOURCES
    if db_source == "import":
        return "source = ?", IMPORT_SOURCES
    placeholders = ",".join(["?"] * len(REAL_SOURCES))
    return f"source IN ({placeholders})", REAL_SOURCES
