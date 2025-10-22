#!/usr/bin/env python3
"""
Prepare a Bedrock Agent and (optionally) route an alias to the prepared version.

Usage:
  python scripts/prepare_and_route.py --agent-id XFIYTNINMT --alias-id TSTALIASID --region us-east-1
"""
import argparse
import json
import time
from typing import Optional

import boto3
from botocore.exceptions import ClientError


def prepare_agent(client, agent_id: str) -> str:
    """Trigger prepare-agent; returns hinted version if available."""
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
        time.sleep(min(2, max(0.5, (time.time() - start) / 30)))


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
    p = argparse.ArgumentParser(description="Prepare Bedrock Agent and route alias")
    p.add_argument("--agent-id", required=True)
    p.add_argument("--alias-id", default=None, help="Optional: alias id to route after prepare")
    p.add_argument("--region", default=None)
    args = p.parse_args()

    session = boto3.Session(region_name=args.region) if args.region else boto3.Session()
    client = session.client("bedrock-agent")

    # Prepare
    ver_hint = prepare_agent(client, args.agent_id)
    print(json.dumps({"prepareTriggered": True, "hintVersion": ver_hint}), flush=True)

    # Wait
    version = wait_for_prepared(client, args.agent_id)
    print(json.dumps({"preparedVersion": version}), flush=True)

    # Route alias if provided
    if args.alias_id:
        route_alias_to_version(client, args.agent_id, args.alias_id, version)
        print(json.dumps({"aliasRouted": True, "aliasId": args.alias_id, "agentVersion": version}), flush=True)


if __name__ == "__main__":
    main()
