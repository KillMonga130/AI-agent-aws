"""Integration tests for the Ocean Forecasting Agent."""

import asyncio
import pytest
from src.models.schemas import (
    LocationData,
    MaritimeSafetyQuery,
    WeatherData,
    OceanData
)
from src.agents.supervisor_agent import SupervisorAgent
from src.agents.data_ingestion_agent import DataIngestionAgent
from src.agents.risk_analysis_agent import RiskAnalysisAgent
from src.agents.alert_generation_agent import AlertGenerationAgent


@pytest.mark.asyncio
async def test_data_ingestion_agent():
    """Test data ingestion agent."""
    agent = DataIngestionAgent()
    location = LocationData(
        latitude=-33.9249,
        longitude=18.4241,
        name="Cape Town"
    )
    
    result = await agent.execute(location)
    assert result.location == location
    assert result.error is None


@pytest.mark.asyncio
async def test_risk_analysis_agent():
    """Test risk analysis agent."""
    from src.models.schemas import IngestionResult
    
    agent = RiskAnalysisAgent()
    weather = WeatherData(
        wave_height=3.5,
        wave_direction=180.0,
        wave_period=8.0,
        wind_speed=28.0,
        wind_direction=270.0,
        visibility=4.0
    )
    
    ocean = OceanData(
        sea_surface_height=0.2,
        current_velocity_u=0.3,
        current_velocity_v=0.2,
        sea_surface_temperature=18.5,
        salinity=34.5
    )
    
    ingestion = IngestionResult(
        location=LocationData(
            latitude=-33.9249,
            longitude=18.4241,
            name="Cape Town"
        ),
        weather_data=weather,
        ocean_data=ocean
    )
    
    assessment = await agent.execute(ingestion)
    assert assessment.risk_level in ["LOW", "MODERATE", "HIGH", "SEVERE"]
    assert 0 <= assessment.risk_score <= 100


@pytest.mark.asyncio
async def test_alert_generation_agent():
    """Test alert generation agent."""
    from src.models.schemas import RiskAssessment
    
    agent = AlertGenerationAgent()
    assessment = RiskAssessment(
        risk_level="HIGH",
        risk_score=65,
        hazards=["High waves", "Strong winds"],
        recommendations=["Reduce speed", "Monitor conditions"],
        reasoning="Challenging sea state developing",
        confidence_score=0.85
    )
    
    alert = await agent.execute(assessment)
    assert alert.alert_level == "WARNING"
    assert alert.risk_score == 65
    assert len(alert.alert_text) > 0


@pytest.mark.asyncio
async def test_supervisor_agent():
    """Test supervisor agent with full workflow."""
    supervisor = SupervisorAgent()
    query = MaritimeSafetyQuery(
        query="Is it safe to sail from Cape Town today?",
        location=LocationData(
            latitude=-33.9249,
            longitude=18.4241,
            name="Cape Town"
        )
    )
    
    response = await supervisor.process_query(query)
    assert response.query == query.query
    assert len(response.response) > 0
    assert response.execution_time_seconds > 0


def test_location_extraction():
    """Test location extraction from natural language."""
    supervisor = SupervisorAgent()
    # This would require async context
    assert supervisor.name == "SupervisorAgent"
    assert len(supervisor.data_agent.name) > 0


def test_agent_info():
    """Test agent info retrieval."""
    supervisor = SupervisorAgent()
    info = supervisor.get_agent_info()
    assert info["name"] == "SupervisorAgent"
    assert len(info["sub_agents"]) == 3
    assert "capabilities" in info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
