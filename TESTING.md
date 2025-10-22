# Testing Guide for Autonomous Ocean Forecasting Agent

## Local Testing (No AWS Required)

### 1. Test Demo Mode UI
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run Streamlit in demo mode
streamlit run app.py
```

**Test Cases:**
- ✅ Load interface successfully
- ✅ Select preset location (Cape Town)
- ✅ Enable "Demo Mode" checkbox
- ✅ Click "Analyze Ocean Conditions"
- ✅ Verify mock response displays correctly
- ✅ Check color-coded severity indicators (🔴🟡🟢)
- ✅ Test query history tracking

### 2. Test Lambda Function Locally
```powershell
python data_ingestion_lambda.py
```

**Expected Output:**
```json
{
  "statusCode": 200,
  "data_key": "ocean-data/20251022_120000_Cape_Town_Harbor.json",
  "bucket": "ocean-forecast-data-hackathon",
  "location": "Cape Town Harbor",
  "timestamp": "2025-10-22T12:00:00"
}
```

### 3. Test Agent Locally
```powershell
python ocean_forecast_agent.py
```

**Expected Output:**
- Agent loads successfully
- Tools registered correctly
- Test query processed
- Response generated

## AWS Integration Testing

### 1. Test Lambda in AWS
```powershell
# Invoke Lambda function
aws lambda invoke `
  --function-name OceanDataIngestionLambda `
  --payload '{"location": {"lat": -33.9249, "lon": 18.4241, "name": "Cape Town"}}' `
  --region us-east-1 `
  response.json

# Check response
cat response.json
```

### 2. Verify S3 Data Storage
```powershell
# List objects in bucket
aws s3 ls s3://ocean-forecast-data-hackathon/ocean-data/ --recursive

# Download and inspect a file
aws s3 cp s3://ocean-forecast-data-hackathon/ocean-data/latest.json ./test-data.json
cat test-data.json
```

### 3. Test AgentCore Deployment
```powershell
# Check agent status
agentcore status

# Test agent invocation
agentcore invoke --prompt "What are ocean conditions at Cape Town?"
```

### 4. Test Agent via AWS CLI
```powershell
aws bedrock-agent-runtime invoke-agent `
  --agent-id YOUR_AGENT_ID `
  --agent-alias-id DEFAULT `
  --session-id test-session-1 `
  --input-text "Analyze maritime safety for Singapore Strait at coordinates 1.25, 103.85" `
  --region us-east-1 `
  output.json
```

## End-to-End Testing

### Test Scenario 1: Safe Conditions
**Location:** Caribbean Sea (calm waters)
**Expected:** 🟢 FAVORABLE CONDITIONS

### Test Scenario 2: Moderate Risk
**Location:** North Sea (moderate waves)
**Expected:** 🟡 CAUTION/ADVISORY

### Test Scenario 3: Dangerous Conditions
**Location:** Drake Passage (severe conditions)
**Expected:** 🔴 SEVERE/DANGEROUS

## Integration Testing

### Test Open-Meteo API
```python
import requests

url = "https://marine-api.open-meteo.com/v1/marine"
params = {
    "latitude": -33.9249,
    "longitude": 18.4241,
    "hourly": "wave_height,wave_direction"
}

response = requests.get(url, params=params)
print(response.json())
```

### Test Copernicus Marine (Requires Authentication)
```python
import copernicusmarine

# Login first
copernicusmarine.login()

# Test data retrieval
dataset = copernicusmarine.open_dataset(
    dataset_id="cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m",
    minimum_longitude=18.0,
    maximum_longitude=19.0,
    minimum_latitude=-34.0,
    maximum_latitude=-33.0
)

print(dataset)
```

## Performance Testing

### Load Testing (Optional)
```python
import concurrent.futures
import time

def test_query(location):
    # Simulate multiple concurrent queries
    start = time.time()
    # Make API call
    end = time.time()
    return end - start

locations = [
    (-33.9249, 18.4241),  # Cape Town
    (1.2500, 103.8500),   # Singapore
    (27.5000, -90.0000),  # Gulf of Mexico
]

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(test_query, loc) for loc in locations * 10]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]

print(f"Average response time: {sum(results)/len(results):.2f}s")
```

## Error Testing

### Test Invalid Coordinates
```python
# Should handle gracefully
test_cases = [
    (999, 999),      # Out of range
    (None, None),    # Null values
    ("abc", "def"),  # Invalid types
]

for lat, lon in test_cases:
    try:
        # Test agent with invalid input
        print(f"Testing {lat}, {lon}")
    except Exception as e:
        print(f"Error handled: {e}")
```

### Test API Failures
```python
# Simulate API timeout
# Verify fallback behavior
# Check error messages are user-friendly
```

## User Acceptance Testing

### Usability Checklist
- [ ] Interface loads within 3 seconds
- [ ] Location selection is intuitive
- [ ] Query templates cover common use cases
- [ ] Results are easy to understand
- [ ] Severity levels are visually clear
- [ ] Recommendations are actionable
- [ ] History is accessible
- [ ] Demo mode works without AWS

### Accessibility Testing
- [ ] Color contrast meets WCAG standards
- [ ] Text is readable (font size, spacing)
- [ ] Buttons are clearly labeled
- [ ] Error messages are helpful
- [ ] Works on mobile browsers

## Pre-Submission Testing

### Final Checklist
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Demo mode works perfectly
- [ ] AWS deployment successful
- [ ] Agent responds correctly to queries
- [ ] No errors in CloudWatch logs
- [ ] S3 data storage confirmed
- [ ] Web interface accessible publicly
- [ ] Video demo records smoothly
- [ ] README instructions work

## Test Data

### Sample Test Queries
```
1. "What are current conditions at Cape Town Harbor?"
2. "Is it safe for small boats at Singapore Strait today?"
3. "Provide 5-day forecast for Gulf of Mexico"
4. "Analyze wave heights and currents at Port of Santos"
5. "Are there any severe weather warnings for English Channel?"
```

### Expected Response Format
```
MARITIME RISK ANALYSIS - Location Name
========================================

OVERALL ASSESSMENT:
[🔴/🟡/🟢] [Severity Level]
(Risk Score: X/10)

DETAILED RISKS:
• [Risk 1]
• [Risk 2]
• [Risk 3]

DATA TIMESTAMP: [ISO timestamp]

========================================
MARITIME SAFETY [ALERT TYPE]
========================================

RECOMMENDED ACTIONS:
• [Action 1]
• [Action 2]
• [Action 3]

FORECAST VALIDITY:
Issued: [timestamp]
Valid Until: [timestamp]
```

## Debug Tools

### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Lambda Logs
```powershell
aws logs tail /aws/lambda/OceanDataIngestionLambda --follow
```

### Monitor AgentCore
```powershell
agentcore logs --follow
```

### Streamlit Debug Mode
```powershell
streamlit run app.py --logger.level=debug
```

## Testing Metrics

Track these metrics:
- ✅ Response time (target: <5 seconds)
- ✅ Success rate (target: >95%)
- ✅ Error rate (target: <5%)
- ✅ User satisfaction (subjective)

## Sign-Off

Before submission:
- [ ] All critical tests passed
- [ ] No blocking bugs
- [ ] Demo works end-to-end
- [ ] Documentation accurate
- [ ] Ready for judges to test

**Tested By:** ___________________
**Date:** ___________________
**Status:** READY FOR SUBMISSION ✅
