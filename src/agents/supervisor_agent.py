"""Supervisor Agent - orchestrates multi-agent workflow using Bedrock AgentCore."""

import logging
import asyncio
import time
from datetime import datetime
from typing import Optional, Dict, Any
from src.models.schemas import (
    MaritimeSafetyQuery,
    LocationData,
    AgentResponse,
    IngestionResult
)
from src.agents.data_ingestion_agent import DataIngestionAgent
from src.agents.risk_analysis_agent import RiskAnalysisAgent
from src.agents.alert_generation_agent import AlertGenerationAgent
from src.services.aws_services import bedrock_client

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """
    Supervisor agent that orchestrates the multi-agent workflow.
    Uses Bedrock AgentCore for reasoning and coordination.
    """
    
    def __init__(self):
        """Initialize the supervisor agent."""
        self.name = "SupervisorAgent"
        self.data_agent = DataIngestionAgent()
        self.risk_agent = RiskAnalysisAgent()
        self.alert_agent = AlertGenerationAgent()
        self.sessions: Dict[str, Dict[str, Any]] = {}  # In-memory session storage
    
    async def process_query(self, query: MaritimeSafetyQuery) -> AgentResponse:
        """
        Process a user query by orchestrating all agents.
        
        Args:
            query: User's maritime safety query
            
        Returns:
            Agent response with alert and analysis
        """
        start_time = time.time()
        logger.info(f"{self.name} processing query: {query.query}")
        
        try:
            # Step 1: Query understanding and location extraction
            location = query.location or await self._extract_location_from_query(query.query)
            
            if not location:
                return AgentResponse(
                    query=query.query,
                    response="Could not determine location from query. Please provide coordinates or location name.",
                    execution_time_seconds=time.time() - start_time,
                    session_id=query.session_id
                )
            
            # Step 2: Data ingestion
            logger.info(f"{self.name} delegating to DataIngestionAgent")
            ingestion_result = await self.data_agent.execute(location)
            
            if ingestion_result.error:
                return AgentResponse(
                    query=query.query,
                    response=f"Data retrieval failed: {ingestion_result.error}",
                    execution_time_seconds=time.time() - start_time,
                    session_id=query.session_id
                )
            
            # Step 3: Risk analysis
            logger.info(f"{self.name} delegating to RiskAnalysisAgent")
            risk_assessment = await self.risk_agent.execute(ingestion_result)
            
            # Step 4: Alert generation
            logger.info(f"{self.name} delegating to AlertGenerationAgent")
            alert = await self.alert_agent.execute(risk_assessment)
            
            # Step 5: Synthesize response
            response_text = await self._synthesize_response(
                query.query,
                ingestion_result,
                risk_assessment,
                alert
            )
            
            execution_time = time.time() - start_time
            logger.info(f"{self.name} completed in {execution_time:.2f}s")
            
            return AgentResponse(
                query=query.query,
                response=response_text,
                alert=alert,
                data_sources=["Copernicus Marine", "Open-Meteo Marine"],
                execution_time_seconds=execution_time,
                session_id=query.session_id,
                agent_traces={
                    "ingestion": {
                        "location": location.model_dump(),
                        "weather_available": ingestion_result.weather_data is not None,
                        "ocean_available": ingestion_result.ocean_data is not None
                    },
                    "risk_assessment": {
                        "risk_level": risk_assessment.risk_level,
                        "risk_score": risk_assessment.risk_score,
                        "confidence": risk_assessment.confidence_score
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"{self.name} failed: {e}")
            execution_time = time.time() - start_time
            return AgentResponse(
                query=query.query,
                response=f"An error occurred during analysis: {str(e)}",
                execution_time_seconds=execution_time,
                session_id=query.session_id
            )
    
    async def _extract_location_from_query(self, query_text: str) -> Optional[LocationData]:
        """
        Extract location from natural language query using LLM.
        
        Args:
            query_text: User's natural language query
            
        Returns:
            LocationData or None if extraction fails
        """
        prompt = f"""
Extract location information from this maritime query:
"{query_text}"

If the query mentions specific locations, extract them.
Respond with JSON: {{"location_name": "name", "latitude": X, "longitude": Y}}

If no location found, use Cape Town, South Africa as default: 
{{"location_name": "Cape Town, South Africa", "latitude": -33.9249, "longitude": 18.4241}}
"""
        
        try:
            response_text = bedrock_client.invoke_model(
                prompt=prompt,
                max_tokens=256,
                temperature=0.1
            )
            
            import json
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return LocationData(
                    latitude=data["latitude"],
                    longitude=data["longitude"],
                    name=data.get("location_name", "Unknown")
                )
        except Exception as e:
            logger.warning(f"Location extraction failed: {e}, using default")
        
        # Default to Cape Town
        return LocationData(
            latitude=-33.9249,
            longitude=18.4241,
            name="Cape Town, South Africa (default)"
        )
    
    async def _synthesize_response(
        self,
        original_query: str,
        ingestion: IngestionResult,
        assessment,
        alert
    ) -> str:
        """Synthesize a comprehensive response from all analysis."""
        
        prompt = f"""
Based on this maritime query and analysis, provide a clear, actionable response.

Query: {original_query}
Location: {ingestion.location.name} ({ingestion.location.latitude}, {ingestion.location.longitude})

Alert Level: {alert.alert_level}
Risk Assessment: {assessment.risk_level}
Confidence: {assessment.confidence_score:.0%}

Key Hazards:
{chr(10).join(f"- {h}" for h in assessment.hazards[:3])}

Recommendations:
{chr(10).join(f"- {r}" for r in assessment.recommendations[:3])}

Provide a brief, natural language response that directly answers the user's query,
incorporating the alert and recommendations. Be concise but thorough.
"""
        
        try:
            response = bedrock_client.invoke_model(
                prompt=prompt,
                max_tokens=512,
                temperature=0.7,
                system_prompt="You are a maritime safety expert communicating with vessel operators."
            )
            return response
        except Exception as e:
            logger.warning(f"Response synthesis failed: {e}")
            return alert.alert_text
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Return information about the supervisor agent."""
        return {
            "name": self.name,
            "type": "Supervisor",
            "sub_agents": [
                self.data_agent.name,
                self.risk_agent.name,
                self.alert_agent.name
            ],
            "capabilities": [
                "Maritime safety query understanding",
                "Multi-agent orchestration",
                "Risk assessment coordination",
                "Alert generation and synthesis"
            ],
            "session_count": len(self.sessions)
        }
