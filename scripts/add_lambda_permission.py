#!/usr/bin/env python3
"""
Grant Lambda invoke permission to the Bedrock Agent execution role.

Usage:
  python scripts/add_lambda_permission.py --function-name ocean-agent-ingest --agent-id XFIYTNINMT --region us-east-1
"""
import argparse
import json
import sys
import boto3
from botocore.exceptions import ClientError


def add_permission(lambda_client, function_name: str, agent_id: str, account_id: str, region: str):
    """Add resource policy to Lambda allowing Bedrock agent to invoke it."""
    statement_id = f"AllowBedrockAgent{agent_id}"
    source_arn = f"arn:aws:bedrock:{region}:{account_id}:agent/{agent_id}"
    
    try:
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=statement_id,
            Action="lambda:InvokeFunction",
            Principal="bedrock.amazonaws.com",
            SourceArn=source_arn,
        )
        return {"success": True, "statementId": statement_id}
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "ResourceConflictException":
            return {"success": True, "message": "Permission already exists"}
        raise


def main():
    p = argparse.ArgumentParser(description="Grant Lambda invoke permission to Bedrock Agent")
    p.add_argument("--function-name", required=True, help="Lambda function name")
    p.add_argument("--agent-id", required=True, help="Bedrock Agent ID")
    p.add_argument("--region", default=None)
    args = p.parse_args()

    session = boto3.Session(region_name=args.region) if args.region else boto3.Session()
    lambda_client = session.client("lambda")
    sts_client = session.client("sts")
    
    account_id = sts_client.get_caller_identity()["Account"]
    region = session.region_name or "us-east-1"
    
    result = add_permission(lambda_client, args.function_name, args.agent_id, account_id, region)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
