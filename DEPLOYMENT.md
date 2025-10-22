"""Deployment and setup instructions."""

DEPLOYMENT_GUIDE = """
# Ocean Forecasting Agent - Deployment Guide

## Prerequisites

1. **AWS Account** with appropriate permissions
   - IAM permissions for Bedrock, Lambda, S3, API Gateway
   - AWS CLI configured with credentials

2. **Local Development Setup**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials and configuration
   ```

## Deployment Options

### Option 1: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export BEDROCK_MODEL_ID=us.anthropic.claude-3-5-sonnet-20241022-v2:0
export AWS_REGION=us-east-1

# Run the FastAPI server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Access the API at: http://localhost:8000/docs

### Option 2: AWS Lambda (SAM)

```bash
# Install AWS SAM CLI
pip install aws-sam-cli

# Build the application
sam build

# Deploy to AWS (guided mode)
sam deploy --guided

# Provide parameters:
# Stack name: ocean-forecasting-agent
# Region: us-east-1
# S3 bucket: ocean-forecast-data-<your-account-id>
```

### Option 3: Docker Containerization

```bash
# Build Docker image
docker build -t ocean-forecasting-agent .

# Run container locally
docker run -p 8000:8000 \\
  -e BEDROCK_MODEL_ID=us.anthropic.claude-3-5-sonnet-20241022-v2:0 \\
  -e AWS_REGION=us-east-1 \\
  ocean-forecasting-agent

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag ocean-forecasting-agent:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ocean-forecasting-agent:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ocean-forecasting-agent:latest
```

## AWS Bedrock Configuration

### 1. Enable Model Access
```bash
# In AWS Console or via CLI
aws bedrock update-model-access \\
  --region us-east-1 \\
  --model-access-status "Granted" \\
  --model-id "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
```

### 2. Create IAM Role for Bedrock Access
```bash
aws iam attach-role-policy \\
  --role-name OceanForecastingAgentRole \\
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

## Testing the Deployment

### 1. Health Check
```bash
curl http://localhost:8000/health
# or if deployed to AWS
curl https://<api-gateway-url>/health
```

### 2. Query Endpoint
```bash
curl -X POST http://localhost:8000/query \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "Is it safe to sail from Cape Town to Mossel Bay tomorrow?",
    "session_id": "test-session-1"
  }'
```

### 3. Location-Specific Query
```bash
curl -X POST "http://localhost:8000/query/location?query=Is%20it%20safe%20today&latitude=-33.9249&longitude=18.4241&location_name=Cape%20Town" \\
  -H "Content-Type: application/json"
```

## Monitoring

### CloudWatch Logs
```bash
# View agent logs
aws logs tail /aws/lambda/ocean-forecasting-agent --follow

# Query specific errors
aws logs filter-log-events \\
  --log-group-name /aws/lambda/ocean-forecasting-agent \\
  --filter-pattern "ERROR"
```

### Performance Metrics
- Track query latency in CloudWatch
- Monitor Bedrock API usage and costs
- Review S3 data storage patterns

## Scaling Considerations

1. **Concurrency**: Lambda auto-scales to handle parallel queries
2. **API Gateway**: Enable caching for common queries
3. **Bedrock**: Monitor token usage, consider batch processing
4. **S3**: Implement lifecycle policies to manage storage costs

## Cost Optimization

- Bedrock: Monitor token costs ($0.03-$0.30 per 1K tokens)
- Lambda: 1GB-minute = $0.0000166667 (free tier: 1M requests/month)
- S3: Standard storage ~$0.023/GB (first 50TB/month)
- API Gateway: $3.50 per million API calls

## Troubleshooting

### Issue: Bedrock Model Not Accessible
```bash
# Check model access
aws bedrock list-models --region us-east-1

# Request access if needed
# Contact AWS support
```

### Issue: S3 Bucket Permission Denied
```bash
# Verify IAM role has S3 permissions
aws iam get-role-policy --role-name OceanForecastingAgentRole --policy-name S3Access
```

### Issue: Slow Query Response
- Check Lambda memory allocation (increase if needed)
- Review Bedrock API latency
- Enable API Gateway caching

## Production Checklist

- [ ] Enable CloudWatch alarms for errors
- [ ] Set up CloudTrail for audit logging
- [ ] Configure VPC endpoints for private connectivity
- [ ] Implement request/response logging
- [ ] Set up CI/CD pipeline (CodePipeline/CodeBuild)
- [ ] Perform load testing before production
- [ ] Document API schema and authentication
- [ ] Implement rate limiting
- [ ] Set up incident response procedures
"""

if __name__ == "__main__":
    print(DEPLOYMENT_GUIDE)
