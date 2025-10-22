#!/usr/bin/env python3
"""
Create or update a Bedrock Agent action group that binds the ingest Lambda and exposes a tool schema,
then Prepare the Agent and (optionally) route an alias to the prepared version.

Usage (PowerShell):

  # Get values from the stack outputs
  $REGION = "us-east-1"
  $STACK = "ocean-agentcore"
  $INGEST_ARN = (aws cloudformation describe-stacks --stack-name $STACK --query "Stacks[0].Outputs[?OutputKey=='IngestFunctionArn'].OutputValue" --output text --region $REGION)

  # Run the configurator
  python scripts/configure_action_group.py \
    --agent-id <AGENT_ID> \
    --lambda-arn $INGEST_ARN \
    --schema-file schemas/action-groups/fetch_ocean_data.json \
    --action-name fetch_ocean_data \
    --region $REGION \
    --alias-id <AGENT_ALIAS_ID>

Notes:
- This script assumes boto3>=1.26 and Bedrock Agents APIs are available in the region.
- If the action group already exists, it will be updated.
- After creating/updating, it runs PrepareAgent and optionally points the alias to the new prepared version.
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


def upsert_action_group(
    client,
    agent_id: str,
    action_name: str,
    lambda_arn: str,
    parameter_schema: dict,
    description: str = "Fetch ocean and weather data and store to S3 via ingest Lambda.",
) -> str:
    """Create or update an action group with a single function schema mapping to the ingest Lambda.

    Returns the actionGroupId.
    """
    function_schema = {
        "functions": [
            {
                "name": action_name,
                "description": description,
                "parameters": parameter_schema,
            }
        ]
    }

    # Try list to see if it exists
    try:
        paginator = client.get_paginator("list_agent_action_groups")
        for page in paginator.paginate(agentId=agent_id):
            for ag in page.get("actionGroupSummaries", []) or page.get("actionGroups", []):
                # Some SDKs use different keys; try both
                ag_id = ag.get("actionGroupId") or ag.get("id")
                ag_name = ag.get("actionGroupName") or ag.get("name")
                if ag_name == action_name:
                    # Update
                    client.update_agent_action_group(
                        agentId=agent_id,
                        agentVersion="DRAFT",
                        actionGroupId=ag_id,
                        actionGroupName=action_name,
                        description=description,
                        actionGroupExecutor={"lambda": lambda_arn},
                        functionSchema=function_schema,
                        actionGroupState="ENABLED",
                    )
                    return ag_id
    except client.exceptions.ResourceNotFoundException:
        pass
    except Exception:
        # Proceed to create; if list is unsupported in this SDK version, create handles idempotency
        pass

    # Create
    try:
        resp = client.create_agent_action_group(
            agentId=agent_id,
            agentVersion="DRAFT",
            actionGroupName=action_name,
            description=description,
            actionGroupExecutor={"lambda": lambda_arn},
            functionSchema=function_schema,
            actionGroupState="ENABLED",
        )
        ag = resp.get("actionGroup") or resp
        return ag.get("actionGroupId") or ag.get("id")
    except ClientError as e:
        # Surface a clear hint when the SDK model doesn't match service expectations
        print(json.dumps({
            "error": "create_agent_action_group_failed",
            "hint": "Your boto3 SDK may require OpenAPI (apiSchema) or a different functionSchema shape. Consider configuring the action group in the console or provide an OpenAPI spec via S3.",
            "details": str(e),
        }))
        raise


def prepare_agent(client, agent_id: str) -> str:
    resp = client.prepare_agent(agentId=agent_id)
    # May return an agentVersion
    return (resp.get("agent") or {}).get("agentVersion") or resp.get("agentVersion", "")


def wait_for_prepared(client, agent_id: str, timeout_s: int = 600) -> str:
    """Poll get_agent until status is PREPARED; return the latest version string when ready."""
    start = time.time()
    last_status = ""
    version_hint: Optional[str] = None
    while True:
        ga = client.get_agent(agentId=agent_id)
        agent = ga.get("agent", ga)
        status = agent.get("agentStatus") or agent.get("status")
        version_hint = agent.get("agentVersion") or version_hint
        if status != last_status:
            print(json.dumps({"status": status, "version": version_hint or ""}))
            last_status = status
        if status == "PREPARED":
            return version_hint or "DRAFT"
        if time.time() - start > timeout_s:
            raise TimeoutError(f"Agent did not reach PREPARED within {timeout_s}s; last status: {status}")
        _sleep_backoff(1)


def route_alias_to_version(client, agent_id: str, alias_id: str, agent_version: str):
    """Point an alias to the given agent version (or DRAFT)."""
    try:
        client.update_agent_alias(
            agentId=agent_id,
            agentAliasId=alias_id,
            routingConfiguration=[{"agentVersion": agent_version or "DRAFT"}],
        )
    except ClientError as e:
        # Some SDK variants use different field names
        if e.response.get("Error", {}).get("Code") == "ValidationException":
            # Fallback: try string form
            client.update_agent_alias(
                agentId=agent_id,
                agentAliasId=alias_id,
                routingConfiguration=[{"agentVersion": str(agent_version or "DRAFT")}],
            )
        else:
            raise


def main():
    p = argparse.ArgumentParser(description="Configure Bedrock Agent action group and prepare agent")
    p.add_argument("--agent-id", required=True)
    p.add_argument("--lambda-arn", required=True)
    p.add_argument("--schema-file", required=True, help="Path to JSON schema for parameters")
    p.add_argument("--action-name", default="fetch_ocean_data")
    p.add_argument("--alias-id", default=None, help="Optional: alias id to route after prepare")
    p.add_argument("--region", default=None)
    args = p.parse_args()

    with open(args.schema_file, "r", encoding="utf-8") as f:
        param_schema = json.load(f)

    # Ensure the schema is a parameters object (strip top-level $schema/title if present)
    parameters = {
        k: v for k, v in param_schema.items() if k in ("type", "properties", "required", "additionalProperties")
    }
    if not parameters or parameters.get("type") != "object":
        print(json.dumps({"error": "Schema must define an object with properties/required"}))
        sys.exit(2)

    session = boto3.Session(region_name=args.region) if args.region else boto3.Session()
    agent_client = session.client("bedrock-agent")

    # Create or update the action group
    ag_id = upsert_action_group(
        agent_client,
        agent_id=args.agent_id,
        action_name=args.action_name,
        lambda_arn=args.lambda_arn,
        parameter_schema=parameters,
    )
    print(json.dumps({"actionGroupId": ag_id}))

    # Prepare the agent
    ver_hint = prepare_agent(agent_client, args.agent_id)
    print(json.dumps({"prepareTriggered": True, "hintVersion": ver_hint}))

    # Wait for PREPARED
    version = wait_for_prepared(agent_client, args.agent_id)
    print(json.dumps({"preparedVersion": version}))

    # Route alias if provided
    if args.alias_id:
        route_alias_to_version(agent_client, args.agent_id, args.alias_id, version)
        print(json.dumps({"aliasRouted": True, "aliasId": args.alias_id, "agentVersion": version}))


if __name__ == "__main__":
    main()
