"""Alert Generation Agent - synthesizes analysis into actionable alerts."""

import logging
from datetime import datetime
from typing import Optional
from src.models.schemas import RiskAssessment, Alert

logger = logging.getLogger(__name__)


class AlertGenerationAgent:
    """Agent responsible for generating user-friendly maritime alerts."""
    
    def __init__(self):
        """Initialize the alert generation agent."""
        self.name = "AlertGenerationAgent"
    
    async def execute(self, risk_assessment: RiskAssessment) -> Alert:
        """
        Generate actionable alert from risk assessment.
        
        Args:
            risk_assessment: Risk assessment from analysis agent
            
        Returns:
            Alert object with formatted message
        """
        logger.info(f"{self.name} executing for risk level: {risk_assessment.risk_level}")
        
        try:
            alert_level = self._map_risk_to_alert_level(risk_assessment.risk_level)
            alert_text = self._compose_alert_message(risk_assessment, alert_level)
            
            alert = Alert(
                alert_level=alert_level,
                risk_score=risk_assessment.risk_score,
                alert_text=alert_text,
                metrics={
                    "risk_level": risk_assessment.risk_level,
                    "confidence": risk_assessment.confidence_score,
                    "hazards_count": len(risk_assessment.hazards),
                    "recommendations_count": len(risk_assessment.recommendations)
                },
                timestamp=datetime.utcnow()
            )
            
            logger.info(f"{self.name} completed: {alert_level} alert generated")
            return alert
            
        except Exception as e:
            logger.error(f"{self.name} failed: {e}")
            return Alert(
                alert_level="WARNING",
                risk_score=50,
                alert_text="Unable to generate alert. Recommend caution and contact authorities.",
                timestamp=datetime.utcnow()
            )
    
    @staticmethod
    def _map_risk_to_alert_level(risk_level: str) -> str:
        """Map risk assessment level to alert level."""
        mapping = {
            "LOW": "INFORMATIONAL",
            "MODERATE": "ADVISORY",
            "HIGH": "WARNING",
            "SEVERE": "URGENT"
        }
        return mapping.get(risk_level.upper(), "ADVISORY")
    
    @staticmethod
    def _compose_alert_message(assessment: RiskAssessment, alert_level: str) -> str:
        """Compose human-readable alert message."""
        
        header = f"{alert_level} - Maritime Safety Alert"
        
        # Alert level descriptions
        level_descriptions = {
            "INFORMATIONAL": "Safe conditions for all vessel types. Routine monitoring recommended.",
            "ADVISORY": "Proceed with caution. Small craft should monitor closely.",
            "WARNING": "Challenging conditions. Small vessels should postpone. Enhanced monitoring required.",
            "URGENT": "Hazardous conditions. All non-essential operations should cease. Immediate action required."
        }
        
        description = level_descriptions.get(alert_level, "")
        
        # Build hazards section
        hazards_text = ""
        if assessment.hazards:
            hazards_text = "\nIDENTIFIED HAZARDS:\n"
            for i, hazard in enumerate(assessment.hazards[:5], 1):  # Max 5 hazards
                hazards_text += f"  {i}. {hazard}\n"
        
        # Build recommendations section
        recommendations_text = ""
        if assessment.recommendations:
            recommendations_text = "\nRECOMMENDATIONS:\n"
            for i, rec in enumerate(assessment.recommendations[:5], 1):  # Max 5 recommendations
                recommendations_text += f"  {i}. {rec}\n"
        
        # Compose final message
        alert_message = f"""{header}
Issued: {assessment.timestamp.strftime('%Y-%m-%d %H:%M UTC')}
Risk Score: {assessment.risk_score:.0f}/100 (Confidence: {assessment.confidence_score:.0%})

ASSESSMENT:
{description}

ANALYSIS:
{assessment.reasoning}{hazards_text}{recommendations_text}
VALIDITY PERIOD: Next 24 hours
NEXT UPDATE: {(assessment.timestamp.timestamp() + 86400).__repr__()}"""
        
        return alert_message
    
    def get_tool_definitions(self) -> list:
        """Return tool definitions for agent orchestration."""
        return [
            {
                "name": "generate_alert",
                "description": "Generate maritime safety alert from risk assessment",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "risk_level": {
                            "type": "string",
                            "enum": ["LOW", "MODERATE", "HIGH", "SEVERE"],
                            "description": "Risk assessment level"
                        },
                        "risk_score": {
                            "type": "number",
                            "description": "Numerical risk score 0-100"
                        }
                    },
                    "required": ["risk_level", "risk_score"]
                }
            }
        ]
