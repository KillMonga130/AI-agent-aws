"""Risk Analysis Agent - analyzes maritime risks using LLM reasoning."""

import logging
import json
from datetime import datetime
from typing import Optional
from src.models.schemas import IngestionResult, RiskAssessment
from src.services.aws_services import bedrock_client, s3_client

logger = logging.getLogger(__name__)

# Risk thresholds for classification
RISK_THRESHOLDS = {
    "LOW": (0, 25),
    "MODERATE": (25, 50),
    "HIGH": (50, 75),
    "SEVERE": (75, 100)
}


class RiskAnalysisAgent:
    """Agent responsible for analyzing maritime safety risks."""
    
    def __init__(self):
        """Initialize the risk analysis agent."""
        self.name = "RiskAnalysisAgent"
    
    async def execute(self, ingestion_result: IngestionResult) -> RiskAssessment:
        """
        Analyze maritime risks for ingested data.
        
        Args:
            ingestion_result: Data from ingestion agent
            
        Returns:
            RiskAssessment with analysis
        """
        logger.info(f"{self.name} executing for location: {ingestion_result.location}")
        
        if ingestion_result.error:
            return RiskAssessment(
                risk_level="UNKNOWN",
                risk_score=0,
                reasoning="Unable to assess: data ingestion failed",
                confidence_score=0
            )
        
        try:
            # Prepare context for LLM analysis
            context = self._build_analysis_context(ingestion_result)
            
            # Use Bedrock Nova Pro for reasoning
            analysis_prompt = """
Based on the marine conditions provided, analyze the maritime safety risk.

Consider:
1. Wave conditions and their implications for vessel operation
2. Wind patterns and their interaction with waves
3. Ocean currents affecting vessel maneuverability
4. Visibility for safe navigation
5. Compound effects (e.g., waves opposing currents)

Provide:
- Overall risk assessment (LOW/MODERATE/HIGH/SEVERE)
- Risk score (0-100)
- Identified hazards
- Safety recommendations
- Your confidence in this assessment (0-100)

Format response as JSON with keys: risk_level, risk_score, hazards, recommendations, confidence
"""
            
            # Invoke LLM with system context
            system_prompt = """
You are a maritime safety expert with deep knowledge of ocean physics, 
weather patterns, and vessel operations. Analyze conditions to protect human life at sea.

When assessing risk:
- Err on the side of caution for safety
- Consider impacts on different vessel types
- Reference specific thresholds and scientific principles
"""
            
            response_text = bedrock_client.invoke_model(
                prompt=analysis_prompt,
                system_prompt=system_prompt,
                max_tokens=1024,
                temperature=0.3  # Low temperature for consistent risk assessment
            )
            
            # Parse LLM response
            assessment = self._parse_llm_response(response_text, context)
            
            # Store assessment to S3
            s3_key = f"assessments/{ingestion_result.location.latitude}_{ingestion_result.location.longitude}/{datetime.utcnow().isoformat()}.json"
            s3_client.put_object(key=s3_key, data=assessment.model_dump())
            
            logger.info(f"{self.name} completed: {assessment.risk_level} risk")
            return assessment
            
        except Exception as e:
            logger.error(f"{self.name} failed: {e}")
            return RiskAssessment(
                risk_level="HIGH",
                risk_score=75,
                reasoning=f"Error in risk assessment: {str(e)}. Defaulting to caution.",
                confidence_score=0.3
            )
    
    def _build_analysis_context(self, ingestion_result: IngestionResult) -> str:
        """Build context string for LLM analysis."""
        weather = ingestion_result.weather_data
        ocean = ingestion_result.ocean_data
        
        context = f"""
MARINE CONDITIONS REPORT
Location: {ingestion_result.location.name or f"({ingestion_result.location.latitude}, {ingestion_result.location.longitude})"}
Timestamp: {ingestion_result.timestamp.isoformat()}

WEATHER CONDITIONS:
"""
        
        if weather:
            context += f"""- Wave Height: {weather.wave_height:.1f} meters
- Wave Direction: {weather.wave_direction:.0f}° 
- Wave Period: {weather.wave_period:.1f} seconds
- Wind Speed: {weather.wind_speed:.1f} knots
- Wind Direction: {weather.wind_direction:.0f}°
- Visibility: {weather.visibility:.1f} nautical miles
"""
        else:
            context += "- No weather data available\n"
        
        context += "\nOCEAN CONDITIONS:\n"
        if ocean:
            context += f"""- Sea Surface Height: {ocean.sea_surface_height:.2f} meters
- Current Velocity: {ocean.current_velocity_magnitude:.2f} km/h
- Current Direction (U,V): ({ocean.current_velocity_u:.2f}, {ocean.current_velocity_v:.2f}) m/s
- Sea Surface Temperature: {ocean.sea_surface_temperature:.1f}°C
- Salinity: {ocean.salinity:.1f} PSU
"""
        else:
            context += "- No ocean data available\n"
        
        return context
    
    def _parse_llm_response(self, response_text: str, context: str) -> RiskAssessment:
        """Parse LLM response and create RiskAssessment."""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                # Fallback parsing
                data = self._fallback_parse(response_text)
            
            risk_level = data.get("risk_level", "MODERATE").upper()
            risk_score = float(data.get("risk_score", 50))
            
            return RiskAssessment(
                risk_level=risk_level,
                risk_score=min(100, max(0, risk_score)),
                hazards=data.get("hazards", []),
                recommendations=data.get("recommendations", []),
                reasoning=response_text[:500],  # Store first 500 chars
                confidence_score=float(data.get("confidence", 0.7)) / 100.0
            )
        except Exception as e:
            logger.warning(f"Failed to parse LLM response: {e}, using defaults")
            return RiskAssessment(
                risk_level="MODERATE",
                risk_score=50,
                reasoning=response_text,
                confidence_score=0.5
            )
    
    def _fallback_parse(self, response_text: str) -> dict:
        """Fallback parsing when JSON is not properly formatted."""
        result = {
            "risk_level": "MODERATE",
            "risk_score": 50,
            "hazards": [],
            "recommendations": [],
            "confidence": 50
        }
        
        # Simple heuristic parsing
        if "severe" in response_text.lower():
            result["risk_level"] = "SEVERE"
            result["risk_score"] = 80
        elif "high" in response_text.lower() and "risk" in response_text.lower():
            result["risk_level"] = "HIGH"
            result["risk_score"] = 65
        elif "caution" in response_text.lower():
            result["risk_level"] = "MODERATE"
            result["risk_score"] = 45
        
        return result
    
    def get_tool_definitions(self) -> list:
        """Return tool definitions for agent orchestration."""
        return [
            {
                "name": "analyze_maritime_risk",
                "description": "Analyze maritime safety risks from weather and ocean data",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "wave_height": {
                            "type": "number",
                            "description": "Significant wave height in meters"
                        },
                        "wind_speed": {
                            "type": "number",
                            "description": "Wind speed in knots"
                        },
                        "current_velocity": {
                            "type": "number",
                            "description": "Ocean current velocity in km/h"
                        },
                        "visibility": {
                            "type": "number",
                            "description": "Visibility in nautical miles"
                        }
                    }
                }
            }
        ]
