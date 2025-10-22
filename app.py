"""
Streamlit Web Interface for Autonomous Ocean Forecasting Agent
User-friendly frontend for maritime safety predictions
"""

import streamlit as st
import boto3
import json
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Ocean Forecasting Agent",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        padding-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-size: 1.1rem;
        padding: 0.75rem;
        border-radius: 10px;
    }
    .location-card {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

# Header
st.markdown('<h1 class="main-header">🌊 Autonomous Ocean Forecasting Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Maritime Safety Predictions Powered by AI | AWS Bedrock AgentCore</p>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # AWS Configuration
    st.subheader("AWS Settings")
    agent_arn = st.text_input(
        "Agent ARN (optional)",
        value=os.getenv("AGENT_ARN", ""),
        help="Amazon Bedrock AgentCore ARN. Optional if Agent ID + Alias ID are set."
    )

    col_ids1, col_ids2 = st.columns(2)
    with col_ids1:
        agent_id = st.text_input(
            "Agent ID",
            value=os.getenv("AGENT_ID", ""),
            help="From create_agent() output"
        )
    with col_ids2:
        agent_alias_id = st.text_input(
            "Alias ID",
            value=os.getenv("AGENT_ALIAS_ID", ""),
            help="From create_agent_alias() output (e.g., 'prod' alias ID)"
        )
    
    aws_region = st.selectbox(
        "AWS Region",
        ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
        index=0
    )
    
    st.divider()
    
    # About section
    st.subheader("📊 About")
    st.markdown("""
    **Technology Stack:**
    - Amazon Bedrock AgentCore
    - Amazon Nova Pro (Reasoning)
    - Strands Agents Framework
    - Copernicus Marine Service
    - Open-Meteo Marine API
    
    **Capabilities:**
    - Real-time ocean data analysis
    - Wave and current forecasting
    - Maritime risk assessment
    - Autonomous alert generation
    """)
    
    st.divider()
    
    st.subheader("🎯 Hackathon Info")
    st.markdown("""
    **AWS AI Agent Global Hackathon**
    
    Building tomorrow's AI solutions today!
    
    Prize Categories:
    - 🥇 Best AgentCore Implementation
    - 🥈 Best Bedrock Application
    - 🥉 Overall Winners
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📍 Location Input")
    
    # Preset locations
    preset_locations = {
        "Cape Town Harbor, South Africa": (-33.9249, 18.4241),
        "Port of Santos, Brazil": (-23.9500, -46.3167),
        "Singapore Strait": (1.2500, 103.8500),
        "English Channel": (50.0000, -2.0000),
        "Gulf of Mexico": (27.5000, -90.0000),
        "Custom Location": None
    }
    
    selected_location = st.selectbox(
        "Choose Location",
        list(preset_locations.keys())
    )
    
    if preset_locations[selected_location] is not None:
        default_lat, default_lon = preset_locations[selected_location]
    else:
        default_lat, default_lon = 0.0, 0.0
    
    # Coordinate inputs
    latitude = st.number_input(
        "Latitude",
        min_value=-90.0,
        max_value=90.0,
        value=default_lat,
        format="%.4f",
        help="Enter latitude (-90 to 90)"
    )
    
    longitude = st.number_input(
        "Longitude",
        min_value=-180.0,
        max_value=180.0,
        value=default_lon,
        format="%.4f",
        help="Enter longitude (-180 to 180)"
    )
    
    location_name = st.text_input(
        "Location Name",
        value=selected_location if selected_location != "Custom Location" else "Custom Location"
    )

with col2:
    st.subheader("❓ Query Type")
    
    # Predefined queries
    query_templates = {
        "🌊 Current Conditions & Safety Risks": 
            "What are the current ocean conditions and maritime safety risks for {location}?",
        "🚢 Vessel Operation Safety": 
            "Is it safe for fishing vessels to operate at {location} today?",
        "📅 5-Day Maritime Forecast": 
            "Provide a detailed 5-day maritime forecast for {location}.",
        "⚠️ Severe Weather Warnings": 
            "Are there any severe weather warnings or dangerous conditions at {location}?",
        "⛵ Small Vessel Safety": 
            "Evaluate safety conditions for small recreational boats at {location}.",
        "🔍 Detailed Wave Analysis": 
            "Analyze wave heights, periods, and currents for {location}.",
        "✍️ Custom Query": ""
    }
    
    selected_query = st.selectbox(
        "Select Query Type",
        list(query_templates.keys())
    )
    
    if selected_query == "✍️ Custom Query":
        user_query = st.text_area(
            "Enter Custom Query",
            height=100,
            placeholder="Ask about ocean conditions, safety, forecasts, etc."
        )
    else:
        user_query = query_templates[selected_query].format(
            location=f"{location_name} (lat: {latitude}, lon: {longitude})"
        )
        st.text_area("Query Preview", value=user_query, height=100, disabled=True)

# Action buttons
col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])

with col_btn1:
    analyze_button = st.button("🔍 Analyze Ocean Conditions", type="primary", use_container_width=True)

with col_btn2:
    if st.button("🔄 Clear History", use_container_width=True):
        st.session_state.history = []
        st.rerun()

with col_btn3:
    demo_mode = st.checkbox("Demo Mode", value=True, help="Use simulated data for demo")

    auto_monitor = st.checkbox(
        "Autonomous Monitor (every 60s)",
        value=False,
        help="Periodically re-run the analysis to emulate autonomous monitoring"
    )

# Process query
if analyze_button:
    if not user_query.strip():
        st.error("⚠️ Please enter or select a query.")
    elif not (agent_arn or (agent_id and agent_alias_id)) and not demo_mode:
        st.error("⚠️ Please configure Agent (ARN or Agent ID + Alias ID) or enable Demo Mode.")
    else:
        with st.spinner("🤖 Agent is analyzing ocean conditions..."):
            try:
                if demo_mode:
                    # Demo mode - simulate agent response
                    import time
                    time.sleep(2)
                    
                    demo_response = f"""
**MARITIME RISK ANALYSIS - {location_name}**
{'=' * 70}

**OVERALL ASSESSMENT:**
🟡 CHALLENGING CONDITIONS - Proceed with extreme caution
(Risk Score: 5/10)

**DETAILED RISKS:**
• 🟡 CAUTION: Moderate waves at 3.2m - Exercise caution
• ⚠️ WARNING: Short wave period (5.8s) - Choppy, uncomfortable seas
• 🟡 WARNING: Moderate currents at 2.4 km/h - Navigation caution required
• ℹ️ INFO: Sea temperature 18.5°C - Acceptable conditions

**DATA TIMESTAMP:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'=' * 80}
**MARITIME SAFETY ADVISORY**
🟡 ADVISORY
{'=' * 80}

**RECOMMENDED ACTIONS:**
• ⚠️ Proceed with extreme caution - experienced operators only
• 🦺 Ensure all crew wear life jackets
• 📱 Maintain regular communication with shore
• ⏰ Monitor conditions continuously
• 🔄 Have alternate plans ready
• ⛽ Ensure sufficient fuel for unexpected conditions

**FORECAST VALIDITY:**
Issued: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
Valid Until: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
Coverage: Next 24 hours

⚠️  This is an automated AI-generated forecast. Always verify with official 
    maritime authorities and use professional judgment before making decisions.

Generated by: Autonomous Ocean Forecasting Agent
Powered by: Amazon Bedrock AgentCore | Copernicus Marine | Open-Meteo
"""
                    
                    response_text = demo_response
                    
                else:
                    # Production mode - invoke actual Bedrock AgentCore
                    client = boto3.client('bedrock-agent-runtime', region_name=aws_region)

                    # Resolve final IDs
                    resolved_agent_id = (agent_id or (agent_arn.split('/')[-1] if agent_arn else "")).strip()
                    resolved_alias_id = (agent_alias_id or "DEFAULT").strip()
                    if not resolved_agent_id:
                        raise ValueError("Agent ID could not be resolved. Provide Agent ID or Agent ARN.")

                    # Format query with location context
                    full_query = f"{user_query}\n\nLocation: {location_name}\nCoordinates: {latitude}, {longitude}"

                    response = client.invoke_agent(
                        agentId=resolved_agent_id,
                        agentAliasId=resolved_alias_id,
                        sessionId=f"session-{datetime.now().timestamp()}",
                        inputText=full_query
                    )

                    # Parse streaming response (if provided)
                    response_text = ""
                    completion = response.get('completion')
                    if completion:
                        for event in completion:
                            if 'chunk' in event:
                                chunk_text = event['chunk']['bytes'].decode('utf-8')
                                response_text += chunk_text
                    else:
                        # Fallback: some SDKs return outputText directly
                        response_text = response.get('output', {}).get('text', "") or json.dumps(response, indent=2)
                
                # Display response
                st.success("✅ Analysis Complete!")
                st.markdown("---")
                st.markdown(response_text)
                
                # Add to history
                st.session_state.history.append({
                    'timestamp': datetime.now(),
                    'location': location_name,
                    'coordinates': (latitude, longitude),
                    'query': user_query,
                    'response': response_text
                })
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Tip: Configure AWS credentials and Bedrock Agent (Agent ID/Alias), or enable Demo Mode.")

    # Autonomous monitor: refresh the page to re-run every 60 seconds when enabled
    if auto_monitor:
        st.experimental_autorefresh(interval=60_000, key="auto-monitor")

# Display history
if st.session_state.history:
    st.markdown("---")
    st.subheader("📜 Query History")
    
    for idx, item in enumerate(reversed(st.session_state.history[-5:])):  # Show last 5
        with st.expander(f"🕒 {item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {item['location']}"):
            st.markdown(f"**Query:** {item['query']}")
            st.markdown(f"**Coordinates:** {item['coordinates']}")
            st.markdown("**Response:**")
            st.markdown(item['response'])

# Footer
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.metric("🌊 Data Sources", "2 Active", help="Copernicus Marine + Open-Meteo")

with col_footer2:
    st.metric("🤖 Agent Status", "Operational" if demo_mode else "Pending Config")

with col_footer3:
    st.metric("📊 Analyses Run", len(st.session_state.history))

st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p>Built for AWS AI Agent Global Hackathon 2025</p>
    <p>Powered by Amazon Bedrock AgentCore | Strands Agents | Copernicus Marine | Open-Meteo</p>
</div>
""", unsafe_allow_html=True)
