# Ocean Forecasting Agent - Quick Start (AgentCore Edition)

## Current Deployment State ✅
- ✅ Stack deployed: `ocean-agentcore` (us-east-1)
- ✅ Agent created: `XFIYTNINMT` (OceanForecastAgent, amazon.nova-pro-v1:0)
- ✅ Alias created: `TSTALIASID` (AgentTestAlias)
- ✅ Lambda permission granted (Bedrock → ocean-agent-ingest)
- ✅ API Gateway + agent-gateway Lambda live at: `https://aaabp3bu9h.execute-api.us-east-1.amazonaws.com/Prod`

## 🚀 Next 3 Steps to Go Live (10 minutes)

### Step 1: Configure Action Group in Console (5 min)
**Manual step required due to SDK OpenAPI validation strictness.**

1. Go to: https://console.aws.amazon.com/bedrock/home?region=us-east-1#/agents
2. Click **OceanForecastAgent** (XFIYTNINMT)
3. Click **Edit in Agent builder**
4. Scroll to **Action groups** → Click **Add** → **Define with function details**
5. Enter:
   - Name: `fetch_ocean_data`
   - Description: `Fetch ocean and weather data for maritime forecasting`
6. Click **Add function**:
   - Function name: `fetch_ocean_data`
   - Description: `Fetch marine forecast data including waves, wind, currents`
   - **Add 3 parameters**:
     * `latitude` (number, **required**): Latitude coordinate (-90 to 90)
     * `longitude` (number, **required**): Longitude coordinate (-180 to 180)
     * `forecast_hours` (integer, optional): Forecast hours (1-168)
7. **Action group invocation**:
   - Select **Lambda function**
   - Choose: `ocean-agent-ingest`
   - ARN: `arn:aws:lambda:us-east-1:911167913661:function:ocean-agent-ingest`
8. Click **Add** → **Create**

### Step 2: Prepare the Agent (2 min)

**Option A: Console**
1. At the top of Agent page, click **Prepare**
2. Wait for status to change: `PREPARING` → `PREPARED` (1-2 min)

**Option B: Script**
```powershell
cd 'c:\Users\mubva\Downloads\AI agent aws'
.\venv\Scripts\Activate.ps1
python scripts/prepare_and_route.py --agent-id XFIYTNINMT --alias-id TSTALIASID --region us-east-1
```

### Step 3: Test the /query Endpoint (1 min)

```powershell
$API = "https://aaabp3bu9h.execute-api.us-east-1.amazonaws.com/Prod"
$body = '{"query":"Is it safe to sail from Cape Town to Mossel Bay tomorrow?","session_id":"demo-001"}'
Invoke-WebRequest -Method POST -Uri "$API/query" -ContentType application/json -Body $body | Select-Object -ExpandProperty Content
```

**Expected response:**
```json
{
  "response": "Based on the current forecast data for Cape Town to Mossel Bay route... [Agent's maritime analysis]"
}
```

## 🎨 Bonus: Launch Streamlit UI

```powershell
cd 'c:\Users\mubva\Downloads\AI agent aws\streamlit_app'
pip install -r requirements.txt
$env:API_ENDPOINT = "https://aaabp3bu9h.execute-api.us-east-1.amazonaws.com/Prod"
streamlit run app.py
```

Open: http://localhost:8501

---

## 🛠️ Local Development (FastAPI)

If you want to run the FastAPI app locally (not using Bedrock Agents):

### Step 1: Setup
```powershell
cd "c:\Users\mubva\Downloads\AI agent aws"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 2: Configure
```powershell
cp .env.example .env
# Edit .env with your AWS credentials
```

### Step 3: Run
```powershell
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8080
```

Visit: http://127.0.0.1:8080/docs

### Step 4: Test
```powershell
$body = @{
    query = "Is it safe to sail from Cape Town to Mossel Bay tomorrow?"
    session_id = "test-001"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://127.0.0.1:8080/query" -Method Post -ContentType "application/json" -Body $body | Select-Object -ExpandProperty Content
```

## 📦 Deploy to AWS

### Option A: Using SAM (Recommended)
```bash
# Install SAM CLI
pip install aws-sam-cli

# Build
sam build

# Deploy (guided setup)
sam deploy --guided

# Follow prompts for stack name, region, etc.
```

### Option B: Using Docker + ECR
```bash
# Build image
docker build -t ocean-forecasting-agent .

# Test locally
docker run -p 8000:8000 \
  -e AWS_REGION=us-east-1 \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  ocean-forecasting-agent

# Push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag ocean-forecasting-agent:latest \
  <account>.dkr.ecr.us-east-1.amazonaws.com/ocean-forecasting-agent:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/ocean-forecasting-agent:latest
```

## 🧪 Test Examples

### Basic Query
```bash
curl http://localhost:8000/query \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Safe conditions for small boats?"
  }'
```

### With Specific Location
```bash
curl "http://localhost:8000/query/location?query=Safe%20today&latitude=51.5074&longitude=-0.1278&location_name=London"
```

### Health Check
```bash
curl http://localhost:8000/health
```

## 📊 Monitor Performance

### View Logs
```bash
# CloudWatch (if deployed)
aws logs tail /aws/lambda/ocean-forecasting-agent --follow

# Local
python -m uvicorn src.main:app --log-level debug
```

### Check Agent Info
```bash
curl http://localhost:8000/info | jq
```

## 🔧 Troubleshooting

### "Import could not be resolved" warnings
- Ignore if running locally (dependencies installed)
- These resolve when deployed to Lambda

### Bedrock Model Not Accessible
```bash
# Check access
aws bedrock list-models --region us-east-1

# Request access if needed (takes 5 mins)
```

### S3 Permission Denied
```bash
# Verify IAM role has S3 permissions
aws iam get-role-policy \
  --role-name OceanForecastingAgentRole \
  --policy-name S3Access
```

## 📚 Next Steps

1. **Review API Docs**: http://localhost:8000/docs
2. **Read Full Spec**: See `everything.md`
3. **Check Deployment**: See `DEPLOYMENT.md`
4. **Run Tests**: `pytest tests/`
5. **Deploy**: Use SAM or Lambda console

## 🎯 Project Highlights

✅ **Meets Hackathon Requirements**
- ✓ Working AI Agent on AWS
- ✓ Bedrock AgentCore + Nova Pro reasoning
- ✓ Autonomous decision-making
- ✓ Tool integration (APIs, Bedrock)
- ✓ Lambda + S3 + API Gateway

✅ **Production Ready**
- Multi-agent architecture
- Error handling & retry logic
- Logging & monitoring
- Security best practices

✅ **Maritime Impact**
- Real maritime data sources
- Domain expert reasoning
- Actionable alerts
- Cost-effective at scale

## 💡 Tips for Judges

1. **Fast Demo**: Just run `uvicorn` locally, no AWS setup needed
2. **Show Multi-Agent**: Check `/info` endpoint to see all agents
3. **Real Data**: Uses actual Open-Meteo API + mock Copernicus data
4. **LLM Reasoning**: All decisions made by Nova Pro, not rules
5. **Scalable**: Ready for Lambda + API Gateway deployment

---

Questions? Check `README.md` or `DEPLOYMENT.md`
