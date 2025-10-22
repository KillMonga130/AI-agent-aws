# 3‑Minute Demo Script

Goal: Show an end-to-end query hitting the Bedrock Agent via API Gateway and (optionally) data ingest.

## Prep (done beforehand)
- Deployed stack: `ocean-agentcore` (bucket, Lambdas, API)
- Agent + Alias created and wired (env: AGENT_ID/AGENT_ALIAS_ID via SAM deploy)
- Optional: Copernicus secret created

## Run
1) Show stack outputs
   - API URL, Ingest function name, Agent execution role

2) Trigger an ingest (optional)
   - Invoke Lambda with Cape Town coords
   - Show returned S3 key and a glimpse of the object in S3

3) Ask the Agent via HTTP
   - POST {API}/query with: "Is it safe to sail from Cape Town to Mossel Bay tomorrow?"
   - Read aloud the response

4) Show logs
   - CloudWatch logs for agent-gateway Lambda
   - If tools invoked, show ingest Lambda logs

## Script lines
- "We’ve deployed a serverless stack: API Gateway -> Lambda -> Bedrock Agent. The Agent has an action group that can fetch ocean data via our ingest Lambda and store it in S3."
- "Here’s the API URL. Let’s ask a maritime safety question."
- "You can see the structured JSON back, and the answer text."
- "Optionally, I can trigger an ingest for a location; data lands under raw/<lat_lon>/timestamp.json in S3."
- "Finally, here are the logs—everything is traced and structured for quick troubleshooting."
