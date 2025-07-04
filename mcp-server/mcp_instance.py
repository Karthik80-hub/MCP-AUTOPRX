# === File: mcp_instance.py ===
# This file holds the MCP instance to avoid circular imports

import os
import asyncio
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("pr-agent-slack")

# Slack notification hook
async def send_slack_alert(message: str):
    """Send a Slack notification."""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("SLACK_WEBHOOK_URL not set.")
        return

    try:
        import requests
        payload = {
            "text": message,
            "mrkdwn": True
        }
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 200:
            print("Slack notification sent successfully.")
        else:
            print(f"Slack error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception while sending Slack message: {e}")

def on_pr_analysis_complete(summary: str, pr_title: str, repo: str):
    """Hook called after PR analysis is complete."""
    message = f"Claude completed PR analysis for {repo}\n{pr_title}\n\n{summary}"
    asyncio.create_task(send_slack_alert(message))

def on_ci_event_detected(event_type: str, workflow_name: str, status: str, repo: str):
    """Hook called when CI events are detected."""
    if status == "failure":
        message = f"CI Failure Alert - A CI workflow has failed: Workflow: {workflow_name}, Repository: {repo}, Status: Failed. Please check the logs and address any issues."
    elif status == "success":
        message = f"Deployment Successful - Workflow completed successfully: Workflow: {workflow_name}, Repository: {repo}, Status: Success"
    else:
        return
    
    asyncio.create_task(send_slack_alert(message)) 