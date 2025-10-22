"""Utility functions for the agent system."""

import logging
import json
from typing import Any, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for serializing datetime and other types."""
    
    def default(self, obj: Any) -> Any:
        """Encode objects to JSON-serializable types."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "model_dump"):  # Pydantic models
            return obj.model_dump()
        return super().default(obj)


def safe_json_dumps(obj: Any, indent: int = 2) -> str:
    """Safely convert objects to JSON string."""
    return json.dumps(obj, cls=JSONEncoder, indent=indent)


def safe_json_loads(json_str: str) -> Dict[str, Any]:
    """Safely load JSON from string."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return {}


def calculate_current_velocity_magnitude(u: float, v: float) -> float:
    """Calculate current velocity magnitude from u,v components."""
    import math
    magnitude_ms = math.sqrt(u**2 + v**2)
    return magnitude_ms * 3.6  # Convert m/s to km/h


def classify_risk_from_conditions(
    wave_height: float,
    wind_speed: float,
    current_velocity: float,
    visibility: float
) -> Dict[str, Any]:
    """
    Classify maritime risk based on simple thresholds.
    Note: This is a fallback when LLM analysis is unavailable.
    """
    
    risk_score = 0
    hazards = []
    
    # Wave analysis
    if wave_height > 4.0:
        risk_score += 30
        hazards.append("Severe wave conditions (>4m)")
    elif wave_height > 2.5:
        risk_score += 20
        hazards.append("Significant wave conditions (2.5-4m)")
    elif wave_height > 1.5:
        risk_score += 10
    
    # Wind analysis
    if wind_speed > 40:  # Gale force
        risk_score += 30
        hazards.append("Gale-force winds (>40 knots)")
    elif wind_speed > 25:
        risk_score += 15
        hazards.append("Strong winds (25-40 knots)")
    elif wind_speed > 15:
        risk_score += 5
    
    # Current analysis
    if current_velocity > 2.0:
        risk_score += 15
        hazards.append("Strong ocean currents (>2 km/h)")
    elif current_velocity > 1.0:
        risk_score += 8
    
    # Visibility analysis
    if visibility < 1.0:
        risk_score += 25
        hazards.append("Poor visibility (<1 NM)")
    elif visibility < 5.0:
        risk_score += 15
        hazards.append("Moderate visibility (1-5 NM)")
    
    # Map to risk level
    risk_score = min(100, risk_score)
    if risk_score < 25:
        risk_level = "LOW"
    elif risk_score < 50:
        risk_level = "MODERATE"
    elif risk_score < 75:
        risk_level = "HIGH"
    else:
        risk_level = "SEVERE"
    
    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "hazards": hazards
    }


def format_duration(seconds: float) -> str:
    """Format duration in seconds to readable string."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
