#!/usr/bin/env python3
import json
import argparse
import sys
import boto3


def create_agent(client, name: str, model: str, role_arn: str, instruction: str) -> str:
    resp = client.create_agent(
        agentName=name,
        description="Autonomous ocean forecasting agent",
        instruction=instruction,
        foundationModel=model,
        agentResourceRoleArn=role_arn,
    )
    # Newer SDKs return nested object: { "agent": { "agentId": "..." } }
    if "agentId" in resp:
        return resp["agentId"]
    if "agent" in resp and "agentId" in resp["agent"]:
        return resp["agent"]["agentId"]
    raise KeyError("agentId not found in create_agent response")


def create_alias(client, agent_id: str, alias_name: str) -> str:
    resp = client.create_agent_alias(
        agentId=agent_id,
        agentAliasName=alias_name,
    )
    if "agentAliasId" in resp:
        return resp["agentAliasId"]
    if "agentAlias" in resp and "agentAliasId" in resp["agentAlias"]:
        return resp["agentAlias"]["agentAliasId"]
    raise KeyError("agentAliasId not found in create_agent_alias response")


def main():
    parser = argparse.ArgumentParser(description="Create Bedrock Agent and Alias")
    parser.add_argument("--name", default="OceanForecastAgent")
    parser.add_argument("--alias", default="prod")
    parser.add_argument("--model", default="amazon.nova-pro-v1:0", help="Foundation model ID")
    parser.add_argument("--role-arn", required=True, help="Agent execution role ARN (from stack output)")
    parser.add_argument("--instructions-file", required=True, help="Path to system prompt/instructions text file")
    parser.add_argument("--region", default=None)
    args = parser.parse_args()

    with open(args.instructions_file, "r", encoding="utf-8") as f:
        instruction = f.read().strip()

    session = boto3.Session(region_name=args.region) if args.region else boto3.Session()
    client = session.client("bedrock-agent")

    try:
        agent_id = create_agent(client, args.name, args.model, args.role_arn, instruction)
        alias_id = create_alias(client, agent_id, args.alias)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(2)

    print(json.dumps({"agentId": agent_id, "agentAliasId": alias_id}))


if __name__ == "__main__":
    main()
