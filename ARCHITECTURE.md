# Architecture Diagram - Text Version

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                      USER WEB INTERFACE                              │
│                   (Streamlit Dashboard)                              │
│                                                                       │
│  Features:                                                           │
│  • Location selection (preset + custom coordinates)                 │
│  • Query builder (templates + custom)                               │
│  • Real-time results display with color-coded alerts                │
│  • Historical query tracking                                         │
│  • Demo mode for testing without AWS                                │
│                                                                       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTPS/REST API
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│              AMAZON BEDROCK AGENTCORE RUNTIME                        │
│              (Serverless Agent Hosting)                              │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │        STRANDS MULTI-AGENT ORCHESTRATOR                      │  │
│  │        (Amazon Nova Pro - Reasoning LLM)                     │  │
│  │                                                               │  │
│  │  Chain-of-Thought Reasoning:                                 │  │
│  │  1. Parse user query → Extract location & intent             │  │
│  │  2. Fetch ocean data → Call external APIs                    │  │
│  │  3. Analyze risks → Apply safety thresholds                  │  │
│  │  4. Generate alerts → Format actionable recommendations      │  │
│  │                                                               │  │
│  │  ┌─────────────────────────────────────────────────────┐    │  │
│  │  │  AGENT TOOLS (Autonomous Capabilities)              │    │  │
│  │  │                                                      │    │  │
│  │  │  🔧 fetch_current_ocean_data()                      │    │  │
│  │  │     - Invokes Lambda for data ingestion             │    │  │
│  │  │     - Retrieves from S3                             │    │  │
│  │  │     - Returns JSON with ocean + weather data        │    │  │
│  │  │                                                      │    │  │
│  │  │  🔧 analyze_maritime_risks()                        │    │  │
│  │  │     - Analyzes wave heights (>4m = SEVERE)          │    │  │
│  │  │     - Checks current velocities (>2 km/h = WARN)    │    │  │
│  │  │     - Calculates risk score (0-10 scale)            │    │  │
│  │  │     - Returns detailed risk assessment              │    │  │
│  │  │                                                      │    │  │
│  │  │  🔧 generate_forecast_alert()                       │    │  │
│  │  │     - Determines urgency level                       │    │  │
│  │  │     - Creates actionable recommendations            │    │  │
│  │  │     - Formats with severity indicators              │    │  │
│  │  │     - Returns maritime safety alert                 │    │  │
│  │  │                                                      │    │  │
│  │  └─────────────────────────────────────────────────────┘    │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                       │
└────────┬─────────────────────┬─────────────────────┬────────────────┘
         │                     │                     │
         │                     │                     │
         ▼                     ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│                  │  │                  │  │                  │
│   AWS LAMBDA     │  │  COPERNICUS      │  │   OPEN-METEO     │
│  Data Ingestion  │  │  MARINE SERVICE  │  │   MARINE API     │
│                  │  │                  │  │                  │
│  Functions:      │  │  Data:           │  │  Data:           │
│  • Fetch ocean   │  │  • Ocean currents│  │  • Wave heights  │
│  • Fetch weather │  │  • Sea surface   │  │  • Wave periods  │
│  • Combine data  │  │    height        │  │  • Wave direction│
│  • Store in S3   │  │  • Temperature   │  │  • Wind waves    │
│  • Return key    │  │  • Salinity      │  │  • Swell waves   │
│                  │  │  • Global        │  │  • 5-day forecast│
│  Runtime: 60s    │  │    coverage      │  │  • Free API      │
│  Memory: 512MB   │  │                  │  │                  │
│                  │  │                  │  │                  │
└────────┬─────────┘  └──────────────────┘  └──────────────────┘
         │
         │ Store/Retrieve
         │
         ▼
┌──────────────────────────────────────────┐
│                                          │
│         AMAZON S3 BUCKET                 │
│    (Historical Data Storage)             │
│                                          │
│  Storage Structure:                      │
│  ocean-data/                             │
│    ├── 20251022_120000_CapeTown.json    │
│    ├── 20251022_130000_Singapore.json   │
│    └── [timestamp]_[location].json      │
│                                          │
│  Data Retention: 30 days                │
│  Enables: Historical analysis, trends   │
│                                          │
└──────────────────────────────────────────┘


KEY ARCHITECTURAL FEATURES:

1. AUTONOMOUS CAPABILITIES ✅
   • Reasoning LLM (Amazon Nova Pro) for decision-making
   • Zero human intervention required for task execution
   • Self-orchestrating multi-agent workflow
   • Dynamic tool selection based on query context

2. EXTERNAL INTEGRATIONS ✅
   • Copernicus Marine Service API (ocean data)
   • Open-Meteo Marine API (weather forecasts)
   • Amazon S3 (data persistence)
   • AWS Lambda (serverless compute)

3. SCALABILITY ✅
   • Serverless architecture (auto-scaling)
   • AgentCore handles concurrency
   • Lambda processes multiple locations in parallel
   • S3 provides unlimited data storage

4. SAFETY & RELIABILITY ✅
   • Multi-source data validation
   • Risk scoring with defined thresholds
   • Clear severity indicators (🔴🟡🟢)
   • Fallback to cached data if APIs fail

5. HACKATHON REQUIREMENTS ✅
   • Amazon Bedrock AgentCore Runtime ✓
   • Amazon Nova Pro (reasoning) ✓
   • Strands Agents Framework ✓
   • AWS Lambda ✓
   • Amazon S3 ✓
   • External API integrations ✓
   • Autonomous task execution ✓


DATA FLOW:

User Query → AgentCore → Strands Agent → Tools:
  1. fetch_current_ocean_data
     → Lambda → Copernicus + Open-Meteo → S3 → Return JSON
  
  2. analyze_maritime_risks
     → Parse JSON → Calculate risk score → Return assessment
  
  3. generate_forecast_alert
     → Determine urgency → Format alert → Return to user

→ Display in Web UI with color-coded severity


DEPLOYMENT ARCHITECTURE:

Development:
  • Local testing with Demo Mode (no AWS required)
  • Streamlit dev server on localhost:8501

Production:
  • AgentCore deployed in AWS us-east-1
  • Lambda in same region (low latency)
  • S3 bucket with lifecycle policies
  • Streamlit Cloud for web hosting
  • CloudWatch for logging/monitoring


SECURITY:

• IAM roles for Lambda execution
• S3 bucket policies (private)
• AgentCore runtime isolation
• API key management via environment variables
• No sensitive data in code (use .env)
```

## Visual Diagram Creation

To create the visual PNG/SVG diagram:

### Option 1: Use diagrams.net (draw.io)
1. Visit: https://app.diagrams.net/
2. File → New → Blank Diagram
3. Use AWS architecture icons:
   - AWS Bedrock AgentCore (custom shape/text)
   - AWS Lambda (compute icon)
   - Amazon S3 (storage icon)
   - External APIs (cloud icons)
4. Add arrows showing data flow
5. Export as PNG or SVG

### Option 2: Use Python diagrams library
```python
pip install diagrams
python create_architecture_diagram.py
```

### Option 3: Use Lucidchart
1. Visit: https://www.lucidchart.com/
2. Use AWS shape library
3. Drag and drop components
4. Export as image

### Option 4: Use Excalidraw (Quick & Simple)
1. Visit: https://excalidraw.com/
2. Draw boxes and arrows
3. Add text labels
4. Export as PNG

## Recommended Diagram Elements

**Components to Include:**
- User Interface (top)
- Amazon Bedrock AgentCore (center)
- Strands Agent + Tools (inside AgentCore)
- AWS Lambda (left)
- External APIs (right)
- Amazon S3 (bottom)

**Arrows to Show:**
1. User → AgentCore (user input)
2. AgentCore → Lambda (invoke function)
3. Lambda → Copernicus API (fetch ocean data)
4. Lambda → Open-Meteo API (fetch weather)
5. Lambda → S3 (store data)
6. S3 → AgentCore (retrieve data)
7. AgentCore → User (return alert)

**Color Coding:**
- Blue: AWS Services
- Green: External APIs
- Orange: Data Storage
- Purple: User Interface
