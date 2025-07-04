# === File: tools/ci_monitor.py ===

import json
from pathlib import Path
from typing import Optional
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_instance import mcp, on_ci_event_detected

EVENTS_FILE = Path(__file__).parent.parent.parent / "webhook_server" / "github_events.json"

# Define known workflows for this project
KNOWN_WORKFLOWS = {
    "Build documentation": "Main branch documentation build",
    "Build PR Documentation": "Pull request documentation build", 
    "Upload PR Documentation": "PR documentation upload to Hugging Face"
}

@mcp.tool()
async def get_recent_actions_events(limit: int = 10) -> str:
    """Get recent GitHub Actions events received via webhook."""
    if not EVENTS_FILE.exists():
        return json.dumps([])
    with open(EVENTS_FILE, 'r') as f:
        events = json.load(f)
    recent = events[-limit:]
    return json.dumps(recent, indent=2)

@mcp.tool()
async def get_workflow_status(workflow_name: Optional[str] = None) -> str:
    """Get the current status of GitHub Actions workflows."""
    if not EVENTS_FILE.exists():
        return json.dumps({"message": "No GitHub Actions events received yet"})
    with open(EVENTS_FILE, 'r') as f:
        events = json.load(f)
    if not events:
        return json.dumps({"message": "No GitHub Actions events received yet"})

    workflow_events = [e for e in events if e.get("workflow_run") is not None]
    if workflow_name:
        workflow_events = [e for e in workflow_events if e["workflow_run"].get("name") == workflow_name]

    workflows = {}
    for event in workflow_events:
        run = event["workflow_run"]
        name = run["name"]
        if name not in workflows or run["updated_at"] > workflows[name]["updated_at"]:
            workflows[name] = {
                "name": name,
                "status": run["status"],
                "conclusion": run.get("conclusion"),
                "run_number": run["run_number"],
                "updated_at": run["updated_at"],
                "html_url": run["html_url"],
                "description": KNOWN_WORKFLOWS.get(name, "Unknown workflow")
            }
            
            # Trigger Slack notification for new workflow events
            if run.get("conclusion") in ["success", "failure"]:
                repo = event.get("repository", "Unknown")
                on_ci_event_detected("workflow_run", name, run.get("conclusion"), repo)

    return json.dumps(list(workflows.values()), indent=2)

@mcp.tool()
async def get_documentation_workflow_status() -> str:
    """Get the status of documentation-related workflows specifically."""
    if not EVENTS_FILE.exists():
        return json.dumps({"message": "No GitHub Actions events received yet"})
    with open(EVENTS_FILE, 'r') as f:
        events = json.load(f)
    if not events:
        return json.dumps({"message": "No GitHub Actions events received yet"})

    # Filter for documentation workflows
    doc_workflows = ["Build documentation", "Build PR Documentation", "Upload PR Documentation"]
    workflow_events = [
        e for e in events 
        if e.get("workflow_run") and e["workflow_run"].get("name") in doc_workflows
    ]

    workflows = {}
    for event in workflow_events:
        run = event["workflow_run"]
        name = run["name"]
        if name not in workflows or run["updated_at"] > workflows[name]["updated_at"]:
            workflows[name] = {
                "name": name,
                "status": run["status"],
                "conclusion": run.get("conclusion"),
                "run_number": run["run_number"],
                "updated_at": run["updated_at"],
                "html_url": run["html_url"],
                "description": KNOWN_WORKFLOWS.get(name, "Unknown workflow")
            }
            
            # Trigger Slack notification for documentation workflow events
            if run.get("conclusion") in ["success", "failure"]:
                repo = event.get("repository", "Unknown")
                on_ci_event_detected("workflow_run", name, run.get("conclusion"), repo)

    return json.dumps(list(workflows.values()), indent=2)

@mcp.tool()
async def get_failed_workflows() -> str:
    """Get only failed workflows for quick troubleshooting."""
    if not EVENTS_FILE.exists():
        return json.dumps({"message": "No GitHub Actions events received yet"})
    with open(EVENTS_FILE, 'r') as f:
        events = json.load(f)
    if not events:
        return json.dumps({"message": "No GitHub Actions events received yet"})

    workflow_events = [e for e in events if e.get("workflow_run") is not None]
    failed_workflows = [
        e for e in workflow_events 
        if e["workflow_run"].get("conclusion") == "failure"
    ]

    workflows = {}
    for event in failed_workflows:
        run = event["workflow_run"]
        name = run["name"]
        if name not in workflows or run["updated_at"] > workflows[name]["updated_at"]:
            workflows[name] = {
                "name": name,
                "status": run["status"],
                "conclusion": run.get("conclusion"),
                "run_number": run["run_number"],
                "updated_at": run["updated_at"],
                "html_url": run["html_url"],
                "description": KNOWN_WORKFLOWS.get(name, "Unknown workflow")
            }
            
            # Trigger Slack notification for failed workflows
            repo = event.get("repository", "Unknown")
            on_ci_event_detected("workflow_run", name, "failure", repo)

    return json.dumps(list(workflows.values()), indent=2)
