# Bedrock Agent Setup Guide

This guide walks you through connecting your Bedrock Agent to the ingest Lambda, configuring action groups, and testing the /query endpoint.

## Prerequisites
- Stack deployed from `infra/template-agentcore.yaml` (ocean-agentcore)
- Agent created: AgentId `XFIYTNINMT`
- Alias created: AgentAliasId `TSTALIASID`
- Region: us-east-1

## Step 1: Get Stack Outputs

```powershell
$REGION = "us-east-1"
$STACK = "ocean-agentcore"
$INGEST_ARN = (aws cloudformation describe-stacks --stack-name $STACK --query "Stacks[0].Outputs[?OutputKey=='IngestFunctionArn'].OutputValue" --output text --region $REGION)
$API = (aws cloudformation describe-stacks --stack-name $STACK --query "Stacks[0].Outputs[?OutputKey=='ApiInvokeUrl'].OutputValue" --output text --region $REGION)
$ROLE_ARN = (aws cloudformation describe-stacks --stack-name $STACK --query "Stacks[0].Outputs[?OutputKey=='AgentExecutionRoleArn'].OutputValue" --output text --region $REGION)

echo "Ingest Lambda ARN: $INGEST_ARN"
echo "API URL: $API"
echo "Agent Execution Role ARN: $ROLE_ARN"
```

## Step 2: Configure Action Group in Console

**Since automated OpenAPI schema creation is hitting validation issues, use the AWS Console:**

### 2a. Open Bedrock Console
1. Navigate to **Bedrock** → **Agents** → **OceanForecastAgent** (XFIYTNINMT)
2. Click **Edit in Agent builder**

### 2b. Add Action Group
1. Scroll to **Action groups** section
2. Click **Add** → **Define with function details**
3. Enter:
   - **Name**: `fetch_ocean_data`
   - **Description**: `Fetch ocean and weather data for maritime forecasting`
   - **Action group type**: Select **Function details**

### 2c. Configure Function
1. Click **Add function**
2. Enter function details:
   - **Function name**: `fetch_ocean_data`
   - **Description**: `Fetch marine forecast data including waves, wind, currents, and temperature for a given location`
   
3. **Add Parameters**:
   - Parameter 1:
     - Name: `latitude`
     - Type: `number`
     - Description: `Latitude coordinate (-90 to 90)`
     - Required: ☑️
   
   - Parameter 2:
     - Name: `longitude`
     - Type: `number`
     - Description: `Longitude coordinate (-180 to 180)`
     - Required: ☑️
   
   - Parameter 3:
     - Name: `forecast_hours`
     - Type: `integer`
     - Description: `Number of forecast hours (1-168, default 48)`
     - Required: ☐

### 2d. Link Lambda
1. In **Action group invocation**, select **Lambda function**
2. Choose: `ocean-agent-ingest` (from dropdown or paste ARN)
3. Lambda ARN should be: `arn:aws:lambda:us-east-1:911167913661:function:ocean-agent-ingest`

### 2e. Save Action Group
1. Click **Add** to save the function
2. Click **Create** to save the action group

## Step 3: Prepare the Agent

After adding the action group, **prepare the Agent**:

### Option A: AWS Console
1. At the top of the Agent page, click **Prepare**
2. Wait for status to change from `PREPARING` to `PREPARED` (1-2 minutes)
3. Verify the **Working draft** shows the action group

### Option B: CLI
```powershell
aws bedrock-agent prepare-agent --agent-id XFIYTNINMT --region us-east-1

# Poll status
aws bedrock-agent get-agent --agent-id XFIYTNINMT --region us-east-1 --query 'agent.agentStatus' --output text
```

### Option C: Python Script
```powershell
python scripts/prepare_and_route.py --agent-id XFIYTNINMT --alias-id TSTALIASID --region us-east-1
```

## Step 4: Route Alias to Prepared Version

### Console:
1. Go to **Aliases** tab in the Agent
2. Select `AgentTestAlias` (TSTALIASID)
3. Click **Edit**
4. Under **Version routing**, ensure it points to **DRAFT** or the latest prepared version
5. Click **Save**

### CLI:
```powershell
aws bedrock-agent update-agent-alias --agent-id XFIYTNINMT --agent-alias-id TSTALIASID --routing-configuration agentVersion=DRAFT --region us-east-1
```

## Step 5: Test /query Endpoint

```powershell
$API = (aws cloudformation describe-stacks --stack-name ocean-agentcore --query "Stacks[0].Outputs[?OutputKey=='ApiInvokeUrl'].OutputValue" --output text --region us-east-1)
$body = '{"query":"Is it safe to sail from Cape Town to Mossel Bay tomorrow?","session_id":"demo-001"}'

Invoke-WebRequest -Method POST -Uri "$API/query" -ContentType application/json -Body $body | Select-Object -ExpandProperty Content
```

**Expected response:**
```json
{
  "response": "Based on the current forecast data, [Agent's analysis]..."
}
```

## Troubleshooting

### AccessDeniedException
**Cause**: Lambda doesn't have permission to invoke the Agent, or Agent/Alias not ready.

**Fix**:
1. Verify Agent status is `PREPARED`:
   ```powershell
   aws bedrock-agent get-agent --agent-id XFIYTNINMT --region us-east-1 --query 'agent.agentStatus'
   ```

2. Verify alias routing:
   ```powershell
   aws bedrock-agent get-agent-alias --agent-id XFIYTNINMT --agent-alias-id TSTALIASID --region us-east-1
   ```

3. Check CloudWatch Logs for the API Lambda:
   ```powershell
   aws logs tail /aws/lambda/ocean-agent-agent-gateway --follow --region us-east-1
   ```

4. Ensure `AGENT_ID` and `AGENT_ALIAS_ID` env vars are set in the API Lambda:
   ```powershell
   aws lambda get-function-configuration --function-name ocean-agent-agent-gateway --query 'Environment.Variables' --region us-east-1
   ```

### Agent Not Found
**Cause**: Wrong region or incorrect Agent/Alias IDs.

**Fix**:
- Verify you deployed the stack with the correct AgentId/AgentAliasId parameters
- Redeploy if needed:
  ```powershell
  sam deploy --parameter-overrides AgentId=XFIYTNINMT AgentAliasId=TSTALIASID
  ```

### Lambda Permission Issues
**Cause**: Agent execution role can't invoke the ingest Lambda.

**Fix**:
1. Add Lambda invoke permission for Bedrock:
   ```powershell
   aws lambda add-permission --function-name ocean-agent-ingest --statement-id AllowBedrockInvoke --action lambda:InvokeFunction --principal bedrock.amazonaws.com --source-arn arn:aws:bedrock:us-east-1:911167913661:agent/XFIYTNINMT --region us-east-1
   ```

## Step 6: Tighten IAM (Production)

After successful testing, scope the API Lambda's bedrock:InvokeAgent permission to specific resources:

1. Edit `infra/template-agentcore.yaml`
2. Replace `Resource: "*"` with:
   ```yaml
   Resource:
     - !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:agent/${AgentId}"
     - !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:agent-alias/${AgentId}/${AgentAliasId}"
   ```
3. Redeploy:
   ```powershell
   sam build; sam deploy
   ```
