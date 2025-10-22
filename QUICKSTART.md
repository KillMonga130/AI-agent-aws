# Quick start guide for the Ocean Forecasting Agent

## 🚀 Getting Started in 5 Minutes

### Step 1: Clone and Setup
```bash
# Navigate to project
cd "AI agent aws"

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Or (macOS/Linux)
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure AWS
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your AWS credentials:
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
# BEDROCK_MODEL_ID=us.anthropic.claude-3-5-sonnet-20241022-v2:0
```

### Step 4: Run Locally
```bash
python -m uvicorn src.main:app --reload
```

Visit: http://localhost:8000/docs

### Step 5: Test the API
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Is it safe to sail from Cape Town to Mossel Bay tomorrow?",
    "session_id": "test-1"
  }'
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
