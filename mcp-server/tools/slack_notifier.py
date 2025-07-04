# === File: tools/slack_notifier.py ===

import os
import requests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_instance import mcp

@mcp.tool()
async def send_slack_notification(message: str) -> str:
    """Send a formatted notification to the team Slack channel."""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return "Error: SLACK_WEBHOOK_URL environment variable not set"
    try:
        payload = {
            "text": message,
            "mrkdwn": True
        }
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 200:
            return "Message sent successfully to Slack"
        else:
            return f"Failed to send message. Status: {response.status_code}, Response: {response.text}"
    except requests.exceptions.Timeout:
        return "Request timed out. Check your internet connection and try again."
    except requests.exceptions.ConnectionError:
        return "Connection error. Check your internet connection and webhook URL."
    except Exception as e:
        return f"Error sending message: {str(e)}"
