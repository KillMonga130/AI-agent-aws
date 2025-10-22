"""
Autonomous Ocean Forecasting Agent
Multi-agent system using Amazon Bedrock AgentCore and Strands framework
Analyzes real-time ocean data to provide maritime safety alerts
"""

import os
import json
import boto3
from datetime import datetime
from typing import Dict, Any, List
from strands import Agent, tool
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Initialize AWS clients
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')

# Configuration
app = BedrockAgentCoreApp()
MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"  # Amazon Bedrock Nova Pro
BUCKET_NAME = 'ocean-forecast-data-hackathon'
DATA_LAMBDA_NAME = 'OceanDataIngestionLambda'


@tool
def fetch_current_ocean_data(latitude: float, longitude: float, location_name: str = "Unknown Location") -> str:
    """
    Fetch current ocean and marine weather conditions for a specific location.
    
    This tool invokes the data ingestion Lambda to retrieve real-time data from:
    - Copernicus Marine Service (ocean currents, sea surface height, temperature)
    - Open-Meteo Marine API (wave heights, wave periods, forecasts)
    
    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
        location_name: Human-readable location name (e.g., "Cape Town Harbor")
    
    Returns:
        JSON string containing comprehensive ocean and weather data
    """
    try:
        print(f"Fetching ocean data for {location_name} ({latitude}, {longitude})")
        
        # Invoke data ingestion Lambda
        response = lambda_client.invoke(
            FunctionName=DATA_LAMBDA_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps({
                'location': {
                    'lat': latitude,
                    'lon': longitude,
                    'name': location_name
                }
            })
        )
        
        # Parse Lambda response
        result = json.loads(response['Payload'].read())
        
        if result.get('statusCode') != 200:
            return json.dumps({
                'error': 'Failed to fetch ocean data',
                'details': result.get('error', 'Unknown error')
            })
        
        # Retrieve data from S3
        data_key = result['data_key']
        obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=data_key)
        ocean_data = json.loads(obj['Body'].read())
        
        return json.dumps(ocean_data, indent=2)
        
    except Exception as e:
        error_msg = f"Error fetching ocean data: {str(e)}"
        print(error_msg)
        return json.dumps({'error': error_msg})


@tool
def analyze_maritime_risks(ocean_data_json: str) -> str:
    """
    Analyze ocean data to identify maritime safety risks and hazards.
    
    This tool performs comprehensive risk assessment based on:
    - Wave heights and periods (risk of capsizing, sea sickness)
    - Ocean current velocities (navigation hazards, drift)
    - Combined sea conditions (synergistic effects)
    
    Risk Thresholds:
    - Wave Height: >4m SEVERE, >2.5m CAUTION, <2.5m SAFE
    - Current Velocity: >2 km/h WARNING, >3 km/h SEVERE
    - Wave Period: <6s (short, choppy), >15s (long swell)
    
    Args:
        ocean_data_json: JSON string from fetch_current_ocean_data tool
    
    Returns:
        Detailed risk analysis with severity levels and specific hazards
    """
    try:
        data = json.loads(ocean_data_json)
        
        if 'error' in data:
            return f"Cannot analyze risks: {data['error']}"
        
        risks = []
        severity_score = 0  # 0-10 scale
        
        # Extract data
        weather = data.get('marine_weather', {})
        ocean = data.get('ocean_conditions', {})
        location = data.get('location', {})
        
        # Analyze wave conditions
        wave_height = weather.get('wave_height', 0)
        wave_period = weather.get('wave_period', 0)
        wind_wave = weather.get('wind_wave_height', 0)
        swell_wave = weather.get('swell_wave_height', 0)
        
        if wave_height > 4.0:
            risks.append(f"🔴 SEVERE: Wave heights reaching {wave_height}m - DANGEROUS for small vessels")
            severity_score += 4
        elif wave_height > 2.5:
            risks.append(f"🟡 CAUTION: Moderate waves at {wave_height}m - Exercise caution")
            severity_score += 2
        else:
            risks.append(f"🟢 SAFE: Low wave heights at {wave_height}m - Favorable conditions")
        
        # Analyze wave period (short periods = choppy seas)
        if wave_period > 0:
            if wave_period < 6:
                risks.append(f"⚠️ WARNING: Short wave period ({wave_period}s) - Choppy, uncomfortable seas")
                severity_score += 1
            elif wave_period > 15:
                risks.append(f"ℹ️ INFO: Long wave period ({wave_period}s) - Long swell waves")
        
        # Analyze ocean currents
        current_velocity = weather.get('ocean_current_velocity', 0)
        current_direction = weather.get('ocean_current_direction', 0)
        
        if current_velocity > 3:
            risks.append(f"🔴 SEVERE: Strong ocean currents at {current_velocity} km/h ({current_direction}°)")
            severity_score += 3
        elif current_velocity > 2:
            risks.append(f"🟡 WARNING: Moderate currents at {current_velocity} km/h - Navigation caution required")
            severity_score += 1
        
        # Analyze combined conditions
        if wind_wave > 2 and swell_wave > 2:
            risks.append(f"⚠️ WARNING: Combined wind waves ({wind_wave}m) and swell ({swell_wave}m) - Complex sea state")
            severity_score += 2
        
        # Ocean temperature (hypothermia risk)
        sea_temp = ocean.get('sea_surface_temperature', 20)
        if sea_temp < 15:
            risks.append(f"❄️ COLD: Sea temperature {sea_temp}°C - Hypothermia risk if immersed")
            severity_score += 1
        
        # Overall assessment
        if severity_score >= 7:
            overall = "🔴 DANGEROUS CONDITIONS - Maritime operations NOT RECOMMENDED"
        elif severity_score >= 4:
            overall = "🟡 CHALLENGING CONDITIONS - Proceed with extreme caution"
        elif severity_score >= 2:
            overall = "🟢 MODERATE CONDITIONS - Safe for experienced operators"
        else:
            overall = "🟢 FAVORABLE CONDITIONS - Safe for maritime operations"
        
        # Compile report
        risk_report = f"""
MARITIME RISK ANALYSIS - {location.get('name', 'Unknown Location')}
{'=' * 70}

OVERALL ASSESSMENT:
{overall}
(Risk Score: {severity_score}/10)

DETAILED RISKS:
{chr(10).join(f'• {risk}' for risk in risks)}

DATA TIMESTAMP: {data.get('timestamp', 'Unknown')}
"""
        return risk_report.strip()
        
    except Exception as e:
        error_msg = f"Error analyzing risks: {str(e)}"
        print(error_msg)
        return error_msg


@tool
def generate_forecast_alert(risk_analysis: str, forecast_hours: int = 24) -> str:
    """
    Generate actionable maritime forecast alert based on risk analysis.
    
    Creates structured alerts with:
    - Urgency level (URGENT/ADVISORY/INFORMATIONAL)
    - Specific recommendations for vessel operators
    - Safety guidelines and alternative actions
    - Forecast validity period
    
    Args:
        risk_analysis: Output from analyze_maritime_risks tool
        forecast_hours: Hours ahead for forecast validity (default: 24)
    
    Returns:
        Formatted maritime safety alert with clear action items
    """
    try:
        # Determine urgency and actions based on risk analysis
        if "DANGEROUS CONDITIONS" in risk_analysis or "SEVERE" in risk_analysis:
            urgency = "🔴 URGENT"
            alert_level = "MARITIME SAFETY WARNING"
            actions = [
                "❌ POSTPONE all non-essential maritime operations",
                "⚓ Seek safe harbor immediately if at sea",
                "🚢 Secure all vessels with additional mooring lines",
                "📻 Monitor VHF Channel 16 for emergency broadcasts",
                "🆘 Ensure emergency equipment is accessible"
            ]
            validity = "IMMEDIATE - Next 12 hours"
            
        elif "CHALLENGING CONDITIONS" in risk_analysis or "CAUTION" in risk_analysis:
            urgency = "🟡 ADVISORY"
            alert_level = "MARITIME SAFETY ADVISORY"
            actions = [
                "⚠️ Proceed with extreme caution - experienced operators only",
                "🦺 Ensure all crew wear life jackets",
                "📱 Maintain regular communication with shore",
                "⏰ Monitor conditions continuously",
                "🔄 Have alternate plans ready",
                "⛽ Ensure sufficient fuel for unexpected conditions"
            ]
            validity = "Next 24 hours"
            
        elif "MODERATE CONDITIONS" in risk_analysis:
            urgency = "🟢 ADVISORY"
            alert_level = "MARITIME CONDITIONS UPDATE"
            actions = [
                "✅ Conditions suitable for experienced operators",
                "👀 Maintain normal vigilance",
                "📊 Monitor weather updates regularly",
                "🦺 Follow standard safety protocols"
            ]
            validity = "Next 24-48 hours"
            
        else:
            urgency = "🟢 INFORMATIONAL"
            alert_level = "MARITIME CONDITIONS - FAVORABLE"
            actions = [
                "✅ Conditions favorable for maritime operations",
                "🌊 Suitable for all vessel types",
                "📊 Continue monitoring for changes",
                "🦺 Maintain standard safety equipment"
            ]
            validity = "Next 48 hours"
        
        # Generate timestamp
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M UTC')
        valid_until = (now.replace(hour=now.hour + forecast_hours)).strftime('%Y-%m-%d %H:%M UTC')
        
        # Compile alert
        alert = f"""
{'=' * 80}
{alert_level}
{urgency}
{'=' * 80}

{risk_analysis}

{'=' * 80}
RECOMMENDED ACTIONS:
{'=' * 80}
{chr(10).join(actions)}

{'=' * 80}
FORECAST VALIDITY:
{'=' * 80}
Issued: {timestamp}
Valid Until: {valid_until}
Coverage: {validity}

⚠️  This is an automated AI-generated forecast. Always verify with official 
    maritime authorities and use professional judgment before making decisions.

Generated by: Autonomous Ocean Forecasting Agent
Powered by: Amazon Bedrock AgentCore | Copernicus Marine | Open-Meteo
{'=' * 80}
"""
        return alert.strip()
        
    except Exception as e:
        error_msg = f"Error generating alert: {str(e)}"
        print(error_msg)
        return error_msg


# System prompt for the agent
SYSTEM_PROMPT = """You are an autonomous ocean forecasting agent specialized in maritime safety analysis.

Your mission is to protect lives and assets at sea by providing accurate, timely maritime safety assessments.

CAPABILITIES:
1. Fetch real-time ocean data (currents, waves, temperature) from Copernicus Marine Service
2. Retrieve marine weather forecasts from Open-Meteo API
3. Analyze combined conditions to identify maritime risks
4. Generate actionable safety alerts for vessel operators

REASONING PROCESS (Use chain-of-thought):
Step 1: Understand the user's location and specific needs
Step 2: Fetch comprehensive ocean and weather data using fetch_current_ocean_data
Step 3: Analyze risks systematically using analyze_maritime_risks:
   - Examine wave heights and periods (capsizing risk, sea sickness)
   - Assess ocean current velocities (navigation hazards)
   - Consider combined effects and synergistic risks
   - Evaluate temperature (hypothermia risk)
Step 4: Generate clear, actionable alerts using generate_forecast_alert
Step 5: Provide specific recommendations based on vessel type and operation

SAFETY PRIORITIES:
- Always prioritize human safety over economic considerations
- Provide measurable metrics (wave heights in meters, current speeds in km/h)
- Use clear severity levels (SAFE/CAUTION/WARNING/SEVERE/DANGEROUS)
- Include specific actions (not just warnings)
- Consider different vessel types (small boats vs. large ships)

COMMUNICATION STYLE:
- Clear, concise, professional
- Use emojis for quick visual scanning (🔴 danger, 🟡 caution, 🟢 safe)
- Provide both summary and detailed analysis
- Include timestamps and validity periods

Remember: You are autonomous - make decisions and provide recommendations confidently based on data analysis."""


@app.entrypoint
def invoke(payload: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main agent entrypoint for Amazon Bedrock AgentCore
    
    Args:
        payload: Input containing user prompt and optional parameters
        context: AgentCore context object
    
    Returns:
        Agent response with maritime forecast analysis
    """
    try:
        # Extract user query
        user_query = payload.get("prompt", "")
        session_id = payload.get("sessionId", "default-session")
        
        print(f"Processing query: {user_query[:100]}...")
        
        # Initialize agent with tools
        agent = Agent(
            model=MODEL_ID,
            system_prompt=SYSTEM_PROMPT,
            tools=[
                fetch_current_ocean_data,
                analyze_maritime_risks,
                generate_forecast_alert
            ]
        )
        
        # Execute agent reasoning
        result = agent(user_query)
        
        # Extract response text
        response_text = result.message.get('content', [{}])[0].get('text', str(result))
        
        # Log tool calls for debugging
        if hasattr(result, 'tool_calls'):
            print(f"Tools used: {[call.name for call in result.tool_calls]}")
        
        return {
            "response": response_text,
            "sessionId": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Agent execution error: {str(e)}"
        print(error_msg)
        return {
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }


# Entry point for local testing
if __name__ == "__main__":
    # Local test mode
    print("🌊 Ocean Forecasting Agent - Local Test Mode")
    print("=" * 60)
    
    test_payload = {
        "prompt": "What are the current ocean conditions and safety risks for Cape Town Harbor at latitude -33.9249, longitude 18.4241?",
        "sessionId": "test-session"
    }
    
    response = invoke(test_payload, None)
    print(json.dumps(response, indent=2))
    
    # Run the agent
    app.run()
