#!/usr/bin/env python3
"""
Upload OpenAPI schema to S3 and configure a Bedrock Agent action group with it.
Then prepare the Agent and route the alias to the prepared version.

Usage (PowerShell):

  $STACK = "ocean-agentcore"
  $REGION = "us-east-1"
  $BUCKET = (aws cloudformation describe-stacks --stack-name $STACK --query "Stacks[0].Outputs[?OutputKey=='DataBucketName'].OutputValue" --output text --region $REGION)
  $LAMBDA_ARN = (aws cloudformation describe-stacks --stack-name $STACK --query "Stacks[0].Outputs[?OutputKey=='IngestFunctionArn'].OutputValue" --output text --region $REGION)

  python scripts/configure_action_group_openapi.py \
    --agent-id <AGENT_ID> \
    --alias-id <AGENT_ALIAS_ID> \
    --lambda-arn $LAMBDA_ARN \
    --openapi-file schemas/action-groups/fetch_ocean_data_openapi.json \
    --s3-bucket $BUCKET \
    --action-name fetch_ocean_data \
    --region $REGION
"""
import argparse
import json
import sys
import time
from typing import Optional

import boto3
from botocore.exceptions import ClientError


def _sleep_backoff(attempt: int):
    time.sleep(min(2 ** attempt, 15))


def upload_schema_to_s3(s3_client, bucket: str, schema_path: str) -> str:
    """Upload OpenAPI JSON to S3 and return the s3:// URI."""
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_content = f.read()
    key = "bedrock-schemas/fetch_ocean_data_openapi.json"
    s3_client.put_object(Bucket=bucket, Key=key, Body=schema_content.encode("utf-8"), ContentType="application/json")
    return f"s3://{bucket}/{key}"


def upsert_action_group(
    client,
    agent_id: str,
    action_name: str,
    lambda_arn: str,
    schema_s3_uri: str,
    description: str = "Fetch ocean and weather data and store to S3.",
) -> str:
    """Create or update an action group with an OpenAPI schema."""
    # Try listing to see if an action group with this name exists
    try:
        paginator = client.get_paginator("list_agent_action_groups")
        for page in paginator.paginate(agentId=agent_id, agentVersion="DRAFT"):
            for ag in page.get("actionGroupSummaries", []):
                ag_id = ag.get("actionGroupId")
                ag_name = ag.get("actionGroupName")
                if ag_name == action_name:
                    # Update
                    client.update_agent_action_group(
                        agentId=agent_id,
                        agentVersion="DRAFT",
                        actionGroupId=ag_id,
                        actionGroupName=action_name,
                        description=description,
                        actionGroupExecutor={"lambda": lambda_arn},
                        apiSchema={"s3": {"s3BucketName": schema_s3_uri.split("/")[2], "s3ObjectKey": "/".join(schema_s3_uri.split("/")[3:])}},
                        actionGroupState="ENABLED",
                    )
                    return ag_id
    except Exception:
        pass

    # Create
    s3_bucket = schema_s3_uri.split("/")[2]
    s3_key = "/".join(schema_s3_uri.split("/")[3:])
    try:
        resp = client.create_agent_action_group(
            agentId=agent_id,
            agentVersion="DRAFT",
            actionGroupName=action_name,
            description=description,
            actionGroupExecutor={"lambda": lambda_arn},
            apiSchema={"s3": {"s3BucketName": s3_bucket, "s3ObjectKey": s3_key}},
            actionGroupState="ENABLED",
        )
        ag = resp.get("actionGroup") or resp
        return ag.get("actionGroupId") or ag.get("id")
    except ClientError as e:
        print(json.dumps({"error": "create_agent_action_group_failed", "details": str(e)}))
        raise


def prepare_agent(client, agent_id: str) -> str:
    resp = client.prepare_agent(agentId=agent_id)
    return (resp.get("agent") or {}).get("agentVersion") or resp.get("agentVersion", "")


def wait_for_prepared(client, agent_id: str, timeout_s: int = 600) -> str:
    """Poll get_agent until status is PREPARED; return the version when ready."""
    start = time.time()
    last_status = ""
    version_hint: Optional[str] = None
    while True:
        ga = client.get_agent(agentId=agent_id)
        agent = ga.get("agent", ga)
        status = agent.get("agentStatus") or agent.get("status")
        version_hint = agent.get("agentVersion") or version_hint
        if status != last_status:
            print(json.dumps({"status": status, "version": version_hint or ""}), flush=True)
            last_status = status
        if status == "PREPARED":
            return version_hint or "DRAFT"
        if time.time() - start > timeout_s:
            raise TimeoutError(f"Agent did not reach PREPARED within {timeout_s}s; last status: {status}")
        _sleep_backoff(1)


def route_alias_to_version(client, agent_id: str, alias_id: str, agent_version: str):
    """Point an alias to the given agent version."""
    try:
        client.update_agent_alias(
            agentId=agent_id,
            agentAliasId=alias_id,
            routingConfiguration=[{"agentVersion": agent_version or "DRAFT"}],
        )
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "ValidationException":
            client.update_agent_alias(
                agentId=agent_id,
                agentAliasId=alias_id,
                routingConfiguration=[{"agentVersion": str(agent_version or "DRAFT")}],
            )
        else:
            raise


def main():
    p = argparse.ArgumentParser(description="Configure Bedrock Agent action group with OpenAPI schema")
    p.add_argument("--agent-id", required=True)
    p.add_argument("--alias-id", default=None, help="Optional: alias id to route after prepare")
    p.add_argument("--lambda-arn", required=True)
    p.add_argument("--openapi-file", required=True, help="Path to OpenAPI JSON schema")
    p.add_argument("--s3-bucket", required=True, help="S3 bucket to upload schema")
    p.add_argument("--action-name", default="fetch_ocean_data")
    p.add_argument("--region", default=None)
    args = p.parse_args()

    session = boto3.Session(region_name=args.region) if args.region else boto3.Session()
    s3_client = session.client("s3")
    agent_client = session.client("bedrock-agent")

    # Upload schema
    schema_s3_uri = upload_schema_to_s3(s3_client, args.s3_bucket, args.openapi_file)
    print(json.dumps({"schemaUploaded": schema_s3_uri}), flush=True)

    # Create or update action group
    ag_id = upsert_action_group(
        agent_client,
        agent_id=args.agent_id,
        action_name=args.action_name,
        lambda_arn=args.lambda_arn,
        schema_s3_uri=schema_s3_uri,
    )
    print(json.dumps({"actionGroupId": ag_id}), flush=True)

    # Prepare the agent
    ver_hint = prepare_agent(agent_client, args.agent_id)
    print(json.dumps({"prepareTriggered": True, "hintVersion": ver_hint}), flush=True)

    # Wait for PREPARED
    version = wait_for_prepared(agent_client, args.agent_id)
    print(json.dumps({"preparedVersion": version}), flush=True)

    # Route alias if provided
    if args.alias_id:
        route_alias_to_version(agent_client, args.agent_id, args.alias_id, version)
        print(json.dumps({"aliasRouted": True, "aliasId": args.alias_id, "agentVersion": version}), flush=True)


if __name__ == "__main__":
    main()
