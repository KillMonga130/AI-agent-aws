# Quick Start Guide - AWS AI Agent Hackathon

## ⏱️ Fast Track Deployment (30 Minutes)

### Prerequisites Check
- [ ] AWS Account with credits claimed
- [ ] AWS CLI installed and configured
- [ ] Python 3.9+ installed
- [ ] Git installed

### Step 1: Environment Setup (5 minutes)
```powershell
# Clone/navigate to project
cd "c:\Users\mubva\Downloads\AI agent aws"

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 2: AWS Configuration (5 minutes)
```powershell
# Configure AWS
aws configure sso --profile ocean-agent

# Test access
aws sts get-caller-identity --profile ocean-agent

# Set default profile
$env:AWS_PROFILE = "ocean-agent"
$env:AWS_REGION = "us-east-1"
```

### Step 3: Deploy Infrastructure (10 minutes)
```powershell
# Make script executable (Git Bash on Windows)
bash deploy.sh

# OR manual deployment:

# Create S3 bucket
aws s3 mb s3://ocean-forecast-data-hackathon

# Deploy Lambda (create zip first)
Compress-Archive -Path data_ingestion_lambda.py -DestinationPath function.zip -Force

# Create Lambda function
aws lambda create-function `
  --function-name OceanDataIngestionLambda `
  --runtime python3.9 `
  --role arn:aws:iam::YOUR_ACCOUNT:role/OceanAgentLambdaRole `
  --handler data_ingestion_lambda.lambda_handler `
  --zip-file fileb://function.zip `
  --timeout 60
```

### Step 4: Deploy Agent (5 minutes)
```powershell
# Install AgentCore CLI
pip install bedrock-agentcore

# Configure agent
agentcore configure -e ocean_forecast_agent.py

# Deploy
agentcore launch

# Get ARN
agentcore status
```

### Step 5: Test & Run (5 minutes)
```powershell
# Update .env with your Agent ARN
Copy-Item .env.example .env
# Edit .env with your AGENT_ARN

# Run web interface
streamlit run app.py

# Access at http://localhost:8501
```

## 🚨 Quick Troubleshooting

### Issue: Import errors
```powershell
pip install --upgrade -r requirements.txt
```

### Issue: AWS credentials
```powershell
aws configure sso --profile ocean-agent
$env:AWS_PROFILE = "ocean-agent"
```

### Issue: AgentCore not found
```powershell
pip install bedrock-agentcore strands-agents
```

### Issue: Lambda timeout
- Increase Lambda timeout to 60 seconds
- Check VPC configuration (should be None)

## 🎯 Demo Mode (No AWS Required)

For immediate testing without AWS deployment:

```powershell
streamlit run app.py
```

Then in the UI:
1. ✅ Check "Demo Mode" checkbox
2. Select any location
3. Click "Analyze Ocean Conditions"

## 📋 Submission Checklist

Before submitting to Devpost:

- [ ] GitHub repo is PUBLIC
- [ ] README.md complete with setup instructions
- [ ] requirements.txt has all dependencies
- [ ] Architecture diagram created
- [ ] 3-minute demo video recorded
- [ ] Web interface deployed (Streamlit Cloud/Railway)
- [ ] Test full workflow end-to-end

## 🎥 Quick Video Recording

Use OBS Studio or Loom:
1. **0:00-0:30** - Show problem (maritime accidents, data fragmentation)
2. **0:30-1:30** - Demo agent analyzing Cape Town Harbor
3. **1:30-2:30** - Show autonomous capabilities (different locations)
4. **2:30-3:00** - Highlight impact and scalability

## 🚀 Deploy to Streamlit Cloud

1. Push to GitHub
2. Visit: https://streamlit.io/cloud
3. Connect repo: `AI agent aws`
4. Main file: `app.py`
5. Set secrets in Streamlit Cloud:
   - `AGENT_ARN`
   - `AWS_REGION`
   - AWS credentials (if not using demo mode)
6. Deploy

## ⏰ Time Remaining

**Deadline:** October 23, 2025 @ 1:00 AM GMT+1

Convert to your timezone:
- SAST (South Africa): October 23, 2:00 AM
- EST: October 22, 8:00 PM
- PST: October 22, 5:00 PM

## 💡 Pro Tips

1. **Test Demo Mode First** - Verify UI works before AWS setup
2. **Use Demo Mode for Video** - More reliable for recording
3. **Document as You Go** - Add comments to code for clarity
4. **Screenshot Everything** - For architecture diagram
5. **Keep It Simple** - Working agent > perfect code

## 🆘 Emergency Contact

If stuck, check:
- AWS Bedrock AgentCore docs: https://docs.aws.amazon.com/bedrock-agentcore/
- Strands GitHub: https://github.com/aws/strands
- Hackathon Discord/Slack (if available)

## 🎉 You've Got This!

Remember:
- ✅ Domain expertise (marine data)
- ✅ Technical skills (ML + full-stack)
- ✅ Real-world impact (maritime safety)
- ✅ Complete implementation plan

**Just execute step by step. Good luck! 🚀🌊**
