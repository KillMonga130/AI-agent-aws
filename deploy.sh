#!/bin/bash

# Deployment Script for Autonomous Ocean Forecasting Agent
# AWS AI Agent Global Hackathon 2025

set -e  # Exit on error

echo "🌊 Deploying Autonomous Ocean Forecasting Agent to AWS"
echo "======================================================="

# Configuration
REGION=${AWS_REGION:-us-east-1}
BUCKET_NAME="ocean-forecast-data-hackathon-$(date +%s)"
LAMBDA_FUNCTION_NAME="OceanDataIngestionLambda"
LAMBDA_ROLE_NAME="OceanAgentLambdaRole"
AGENT_NAME="ocean-forecast-agent"

echo ""
echo "📋 Configuration:"
echo "  Region: $REGION"
echo "  S3 Bucket: $BUCKET_NAME"
echo "  Lambda Function: $LAMBDA_FUNCTION_NAME"
echo ""

# Step 1: Create S3 Bucket
echo "📦 Step 1/5: Creating S3 bucket for data storage..."
aws s3 mb s3://$BUCKET_NAME --region $REGION || echo "Bucket might already exist"

# Step 2: Create Lambda Execution Role
echo "🔐 Step 2/5: Creating Lambda execution role..."

# Create trust policy
cat > /tmp/lambda-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name $LAMBDA_ROLE_NAME \
  --assume-role-policy-document file:///tmp/lambda-trust-policy.json \
  --region $REGION || echo "Role might already exist"

# Wait for role to be available
sleep 5

# Attach policies
aws iam attach-role-policy \
  --role-name $LAMBDA_ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
  --role-name $LAMBDA_ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Wait for policies to attach
sleep 10

# Step 3: Package and Deploy Lambda
echo "📦 Step 3/5: Packaging and deploying Lambda function..."

# Create deployment package
mkdir -p /tmp/lambda-package
cp data_ingestion_lambda.py /tmp/lambda-package/
cd /tmp/lambda-package

# Install dependencies
pip install requests -t . --quiet

# Update bucket name in Lambda code
sed -i "s/ocean-forecast-data-hackathon/$BUCKET_NAME/g" data_ingestion_lambda.py

# Create zip
zip -r function.zip . > /dev/null

cd -

# Get account ID for role ARN
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${LAMBDA_ROLE_NAME}"

# Deploy Lambda
aws lambda create-function \
  --function-name $LAMBDA_FUNCTION_NAME \
  --runtime python3.9 \
  --role $ROLE_ARN \
  --handler data_ingestion_lambda.lambda_handler \
  --zip-file fileb:///tmp/lambda-package/function.zip \
  --timeout 60 \
  --memory-size 512 \
  --region $REGION || \
aws lambda update-function-code \
  --function-name $LAMBDA_FUNCTION_NAME \
  --zip-file fileb:///tmp/lambda-package/function.zip \
  --region $REGION

echo "✅ Lambda function deployed successfully!"

# Step 4: Deploy Agent to AgentCore
echo "🤖 Step 4/5: Deploying agent to Amazon Bedrock AgentCore..."

# Update agent configuration with bucket name
sed -i "s/ocean-forecast-data-hackathon/$BUCKET_NAME/g" ocean_forecast_agent.py

# Configure AgentCore (interactive)
echo "Configuring AgentCore..."
agentcore configure -e ocean_forecast_agent.py <<EOF


no
EOF

# Launch agent
echo "Launching agent to AgentCore..."
agentcore launch

# Get agent status and ARN
AGENT_STATUS=$(agentcore status)
echo "$AGENT_STATUS"

# Extract Agent ARN (you'll need to parse this from status output)
echo ""
echo "⚠️  IMPORTANT: Copy your Agent ARN from the output above"
echo "   You'll need it for the web interface configuration"

# Step 5: Create .env file
echo "📝 Step 5/5: Creating environment configuration..."

cat > .env <<EOF
# AWS Configuration
AWS_REGION=$REGION
S3_BUCKET=$BUCKET_NAME
LAMBDA_FUNCTION_NAME=$LAMBDA_FUNCTION_NAME

# Agent Configuration (UPDATE THIS WITH YOUR ACTUAL AGENT ARN)
AGENT_ARN=arn:aws:bedrock-agentcore:$REGION:$ACCOUNT_ID:runtime/$AGENT_NAME

# Copernicus Marine (Configure after deployment)
COPERNICUS_USERNAME=your-username
COPERNICUS_PASSWORD=your-password
EOF

echo "✅ Environment file created: .env"

# Step 6: Summary
echo ""
echo "======================================================="
echo "✅ Deployment Complete!"
echo "======================================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Configure Copernicus Marine credentials:"
echo "   copernicusmarine login"
echo ""
echo "2. Update .env file with your Agent ARN from AgentCore status above"
echo ""
echo "3. Install Python dependencies:"
echo "   pip install -r requirements.txt"
echo ""
echo "4. Run the Streamlit web interface:"
echo "   streamlit run app.py"
echo ""
echo "5. Test the agent:"
echo "   python ocean_forecast_agent.py"
echo ""
echo "📊 Deployed Resources:"
echo "  ✅ S3 Bucket: s3://$BUCKET_NAME"
echo "  ✅ Lambda: $LAMBDA_FUNCTION_NAME"
echo "  ✅ IAM Role: $LAMBDA_ROLE_NAME"
echo "  ✅ AgentCore Agent: $AGENT_NAME"
echo ""
echo "🎉 Ready for AWS AI Agent Global Hackathon submission!"
echo ""
