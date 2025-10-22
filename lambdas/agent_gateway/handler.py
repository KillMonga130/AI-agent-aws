import json
import os
import logging
import boto3
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(message)s"))
if not logger.handlers:
    logger.addHandler(handler)

client = boto3.client("bedrock-agent-runtime")


def lambda_handler(event, context):
    body = event.get("body", event)
    if isinstance(body, str):
        try:
            body = json.loads(body or "{}")
        except Exception:
            body = {}

    input_text = body.get("query") or body.get("inputText") or ""
    session_id = body.get("sessionId") or body.get("session_id") or "demo-session"

    agent_id = os.getenv("AGENT_ID")
    agent_alias_id = os.getenv("AGENT_ALIAS_ID")
    if not agent_id or not agent_alias_id:
        return {"statusCode": 500, "body": json.dumps({"error": "Agent ID/Alias not configured"})}

    try:
        resp = client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            enableTrace=True,
            inputText=input_text,
        )
        # Streaming responses come via 'completion'
        chunks = []
        for event in resp.get("completion", []):
            if "chunk" in event:
                chunks.append(event["chunk"]["bytes"].decode("utf-8"))
        text = "".join(chunks) if chunks else ""
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"response": text}),
        }
    except Exception as e:
        logger.error({"msg": "invoke_agent_error", "error": str(e)})
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
