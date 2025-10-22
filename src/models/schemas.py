"""Data models for the Ocean Forecasting Agent."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class LocationData(BaseModel):
    """Location information."""
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    name: Optional[str] = Field(None, description="Location name (e.g., Cape Town)")


class WeatherData(BaseModel):
    """Weather and wave data from Open-Meteo Marine API."""
    wave_height: float = Field(..., description="Significant wave height in meters")
    wave_direction: float = Field(..., description="Wave direction in degrees")
    wave_period: float = Field(..., description="Wave period in seconds")
    wind_speed: float = Field(..., description="Wind speed in knots")
    wind_direction: float = Field(..., description="Wind direction in degrees")
    visibility: float = Field(..., description="Visibility in nautical miles")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OceanData(BaseModel):
    """Ocean physics data from Copernicus Marine Service."""
    sea_surface_height: float = Field(..., description="Sea surface height anomaly in meters")
    current_velocity_u: float = Field(..., description="Current velocity U component in m/s")
    current_velocity_v: float = Field(..., description="Current velocity V component in m/s")
    sea_surface_temperature: float = Field(..., description="Sea surface temperature in Celsius")
    salinity: float = Field(..., description="Sea water salinity in PSU")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def current_velocity_magnitude(self) -> float:
        """Calculate current velocity magnitude in km/h."""
        import math
        magnitude_ms = math.sqrt(self.current_velocity_u**2 + self.current_velocity_v**2)
        return magnitude_ms * 3.6  # Convert m/s to km/h


class IngestionResult(BaseModel):
    """Result from data ingestion agent."""
    location: LocationData
    weather_data: Optional[WeatherData] = None
    ocean_data: Optional[OceanData] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RiskAssessment(BaseModel):
    """Risk assessment from analysis agent."""
    risk_level: str = Field(..., description="Risk level: LOW, MODERATE, HIGH, SEVERE")
    risk_score: float = Field(..., ge=0, le=100, description="Numerical risk score 0-100")
    hazards: List[str] = Field(default_factory=list, description="Identified hazards")
    recommendations: List[str] = Field(default_factory=list, description="Safety recommendations")
    reasoning: str = Field(..., description="Detailed reasoning for assessment")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in assessment")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Alert(BaseModel):
    """Generated alert from alert generation agent."""
    alert_level: str = Field(..., description="Alert level: INFORMATIONAL, ADVISORY, WARNING, URGENT")
    risk_score: float = Field(..., ge=0, le=100)
    alert_text: str = Field(..., description="Human-readable alert message")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Key metrics summary")
    validity_period: int = Field(default=24, description="Alert validity in hours")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MaritimeSafetyQuery(BaseModel):
    """User query for maritime safety assessment."""
    query: str = Field(..., description="Natural language query")
    location: Optional[LocationData] = Field(None, description="Optional specific location")
    session_id: Optional[str] = Field(None, description="Session ID for memory tracking")


class AgentResponse(BaseModel):
    """Response from the supervisor agent."""
    query: str
    response: str = Field(..., description="Main response text")
    alert: Optional[Alert] = None
    data_sources: List[str] = Field(default_factory=list)
    agent_traces: Optional[Dict[str, Any]] = None
    execution_time_seconds: float = Field(..., description="Total execution time")
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
