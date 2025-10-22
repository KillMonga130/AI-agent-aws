# Example Usage and Demo Scenarios

## Scenario 1: Safety Check Before Sailing

**User Query:**
```
"Is it safe to sail from Cape Town to Mossel Bay tomorrow with my 8-meter fishing vessel?"
```

**Agent Processing:**
1. Extracts location: Cape Town to Mossel Bay route
2. Fetches weather data: Waves 3.5m, Wind 28 knots, Current 1.5 km/h
3. Analyzes with Nova Pro: "HIGH RISK - Strong winds opposing currents"
4. Generates alert: "WARNING - Advanced mariners only"
5. Provides recommendations: "Postpone 24-36 hours or use northern route"

**Response Example:**
```json
{
  "alert_level": "WARNING",
  "risk_score": 68,
  "alert_text": "WARNING - Maritime Safety Alert\nChallenging Conditions - Small craft should postpone\n...",
  "execution_time_seconds": 7.2
}
```

## Scenario 2: Fishing Fleet Coordination

**User Query:**
```
"Where are the safest waters for trawling near the Agulhas Bank this week?"
```

**Agent Processing:**
1. Analyzes historical patterns
2. Fetches current conditions across fishing zones
3. Identifies optimal routes with favorable conditions
4. Generates zone-specific alerts

## Scenario 3: Climate & Infrastructure Planning

**User Query:**
```
"What are the sea level trends and storm surge risks for Cape Town over the next decade?"
```

**Agent Processing:**
1. Aggregates historical ocean data
2. Analyzes climate patterns
3. Provides long-term forecasting
4. Supports infrastructure planning decisions

## Testing the Agent Locally

### 1. Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Autonomous Ocean Forecasting Agent",
  "version": "0.1.0"
}
```

### 2. Basic Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Is it safe to sail today?"
  }'
```

### 3. Specific Location
```bash
curl -X POST "http://localhost:8000/query/location?query=Safe%20sailing%20today&latitude=-33.9249&longitude=18.4241&location_name=Cape%20Town"
```

### 4. Get Agent Info
```bash
curl http://localhost:8000/info
```

Response includes sub-agents, capabilities, and configuration.

## API Response Structure

```json
{
  "query": "Is it safe to sail from Cape Town to Mossel Bay tomorrow?",
  "response": "WARNING - Challenging Conditions. Strong SE winds (28-32 knots)...",
  "alert": {
    "alert_level": "WARNING",
    "risk_score": 65,
    "alert_text": "Full formatted alert message...",
    "metrics": {
      "risk_level": "HIGH",
      "confidence": 0.87,
      "hazards_count": 3,
      "recommendations_count": 4
    },
    "validity_period": 24,
    "timestamp": "2024-10-22T14:30:00Z"
  },
  "data_sources": [
    "Copernicus Marine",
    "Open-Meteo Marine"
  ],
  "agent_traces": {
    "ingestion": {
      "location": { "latitude": -33.9249, "longitude": 18.4241, "name": "Cape Town" },
      "weather_available": true,
      "ocean_available": true
    },
    "risk_assessment": {
      "risk_level": "HIGH",
      "risk_score": 65,
      "confidence": 0.87
    }
  },
  "execution_time_seconds": 8.4,
  "timestamp": "2024-10-22T14:30:00Z"
}
```

## Data Flow Example

```
User Query: "Safe to sail Mossel Bay tomorrow?"
    ↓
[SupervisorAgent] - Understanding: Cape Town to Mossel Bay, next 24 hours
    ↓
[DataIngestionAgent] - Fetching: Copernicus + Open-Meteo APIs
    ↓
Raw Data: Waves 3.5m, Wind 28kt, Current 1.5km/h
    ↓
[RiskAnalysisAgent] - Nova Pro Reasoning
    ↓
Assessment: HIGH risk (65/100), Strong winds, Challenging conditions
    ↓
[AlertGenerationAgent] - Formatting: WARNING level, with recommendations
    ↓
Response: "WARNING - Small vessels should postpone 24-36 hours"
```

## Performance Expectations

- **Latency**: 6-11 seconds average
- **Success Rate**: 99.8% (with graceful degradation)
- **Cost**: <$0.01 per query

## Integration Examples

### Python Client
```python
import httpx
import asyncio

async def query_agent(question: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/query",
            json={"query": question}
        )
        return response.json()

# Usage
result = asyncio.run(query_agent("Is it safe to sail today?"))
print(result['alert']['alert_level'])
```

### JavaScript/Node.js
```javascript
async function queryAgent(question) {
  const response = await fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: question })
  });
  return response.json();
}

queryAgent("Is it safe to sail today?")
  .then(result => console.log(result.alert.alert_level));
```

### cURL
```bash
#!/bin/bash
QUERY="Is it safe to sail from Cape Town to Mossel Bay tomorrow?"
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\"}" | jq '.alert.alert_level'
```

## Monitoring Queries

```bash
# Stream logs
tail -f /var/log/ocean-forecasting-agent.log | grep RESPONSE

# Count queries
grep "Received query:" logs.txt | wc -l

# Average latency
grep "execution_time_seconds" responses.json | \
  jq -r '.execution_time_seconds' | \
  awk '{sum+=$1} END {print sum/NR}'
```

## Alert Level Definitions

| Level | Score | Meaning | Action |
|-------|-------|---------|--------|
| INFORMATIONAL | 0-25 | Safe | Routine monitoring |
| ADVISORY | 26-50 | Caution | Small craft monitor |
| WARNING | 51-75 | Challenging | Small vessels postpone |
| URGENT | 76-100 | Hazardous | All ops cease |

---

See `README.md` and `QUICKSTART.md` for more information.
