#!/usr/bin/env python3
"""
Unified server for Railway deployment.
Combines webhook server and MCP server into a single process.
"""

import os
import json
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FastAPI for unified HTTP server
try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    print("FastAPI not available. Install with: pip install fastapi uvicorn")
    FASTAPI_AVAILABLE = False

# MCP imports
try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    print("MCP not available. Install with: pip install mcp")
    MCP_AVAILABLE = False

# Import existing MCP tools and prompts
try:
    import sys
    import os
    # Add the mcp-server directory to Python path
    sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp-server'))
    
    from tools.pr_analysis import analyze_file_changes, get_pr_templates
    from tools.ci_monitor import (
        get_recent_actions_events, 
        get_workflow_status, 
        get_documentation_workflow_status,
        get_failed_workflows
    )
    from tools.slack_notifier import send_slack_notification
    from tools.gmail_notifier import send_gmail_notification
    from prompts.pr_prompts import suggest_template
    from prompts.ci_prompts import format_ci_failure_alert, format_ci_success_summary
    from prompts.review_prompts import (
        analyze_ci_results,
        create_deployment_summary,
        generate_pr_status_report,
        troubleshoot_workflow_failure
    )
    MCP_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"MCP tools not available: {e}")
    MCP_TOOLS_AVAILABLE = False

# Configuration
EVENTS_FILE = Path("github_events.json")
PROCESSED_EVENTS = set()

class UnifiedServer:
    def __init__(self):
        self.app = FastAPI(title="MCP-AutoPRX Unified Server", version="1.0.0")
        self.mcp = FastMCP("unified-pr-agent") if MCP_AVAILABLE else None
        self.setup_routes()
        self.setup_middleware()
        self.setup_mcp_tools()
        
    def setup_middleware(self):
        """Setup CORS for cloud access."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """Setup HTTP routes for both webhooks and LLM access."""
        
        @self.app.get("/")
        async def root():
            return {
                "message": "MCP-AutoPRX Unified Server",
                "version": "1.0.0",
                "status": "running",
                "uptime": time.time(),
                "services": {
                    "webhook": "/webhook/github",
                    "health": "/health",
                    "mcp": "/mcp" if MCP_AVAILABLE else "disabled",
                    "tools": "/tools" if MCP_AVAILABLE else "disabled"
                },
                "documentation": "Available at /docs"
            }
        
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "services": {
                    "webhook": "active",
                    "notifications": "active",
                    "mcp": "active" if MCP_AVAILABLE else "disabled"
                }
            }
        
        @self.app.get("/tools")
        async def list_tools():
            """List available MCP tools for LLMs."""
            if not MCP_AVAILABLE:
                return {"error": "MCP not available"}
            
            tools = [
                {
                    "name": "analyze_file_changes",
                    "description": "Analyze git file changes and generate summaries",
                    "parameters": ["base_branch", "include_diff", "max_diff_lines"]
                },
                {
                    "name": "get_pr_templates",
                    "description": "Get available PR templates for different change types",
                    "parameters": []
                },
                {
                    "name": "suggest_template",
                    "description": "Suggest appropriate PR template based on changes",
                    "parameters": ["changes_summary", "change_type"]
                },
                {
                    "name": "get_recent_actions_events",
                    "description": "Get recent GitHub Actions events",
                    "parameters": ["limit"]
                },
                {
                    "name": "get_workflow_status",
                    "description": "Get current status of GitHub Actions workflows",
                    "parameters": ["workflow_name"]
                },
                {
                    "name": "get_documentation_workflow_status",
                    "description": "Get status of documentation-related workflows",
                    "parameters": []
                },
                {
                    "name": "get_failed_workflows",
                    "description": "Get only failed workflows for troubleshooting",
                    "parameters": []
                },
                {
                    "name": "send_slack_notification",
                    "description": "Send Slack notification",
                    "parameters": ["message"]
                },
                {
                    "name": "send_gmail_notification",
                    "description": "Send Gmail notification",
                    "parameters": ["subject", "message", "recipient"]
                }
            ]
            return {"tools": tools}
        
        @self.app.post("/webhook/github")
        async def github_webhook(request: Request):
            """Handle GitHub webhooks - combines webhook server functionality."""
            try:
                data = await request.json()
                event_type = request.headers.get("X-GitHub-Event", "unknown")
                
                # Store event
                await self.store_event(event_type, data)
                
                # Send automatic notifications
                await self.process_event_notifications(event_type, data)
                
                return {"status": "received", "event_type": event_type}
                
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        if MCP_AVAILABLE:
            @self.app.post("/mcp")
            async def mcp_endpoint(request: Request):
                """Handle MCP requests from LLMs."""
                try:
                    data = await request.json()
                    response = await self.mcp.handle_request(data)
                    return response
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            
            @self.app.post("/call/{tool_name}")
            async def call_tool(tool_name: str, request: Request):
                """Direct tool calling endpoint for LLMs."""
                try:
                    data = await request.json()
                    arguments = data.get("arguments", {})
                    
                    # Call the appropriate tool
                    if tool_name == "analyze_file_changes":
                        result = await self.analyze_file_changes(**arguments)
                    elif tool_name == "get_pr_templates":
                        result = await self.get_pr_templates()
                    elif tool_name == "suggest_template":
                        result = await self.suggest_template(
                            arguments.get("changes_summary", ""),
                            arguments.get("change_type", "feature")
                        )
                    elif tool_name == "get_recent_actions_events":
                        result = await self.get_recent_actions_events(**arguments)
                    elif tool_name == "get_workflow_status":
                        result = await self.get_workflow_status(arguments.get("workflow_name"))
                    elif tool_name == "get_documentation_workflow_status":
                        result = await self.get_documentation_workflow_status()
                    elif tool_name == "get_failed_workflows":
                        result = await self.get_failed_workflows()
                    elif tool_name == "send_slack_notification":
                        result = await self.send_slack_message(arguments.get("message", ""))
                    elif tool_name == "send_gmail_notification":
                        result = await self.send_gmail_message(
                            arguments.get("subject", ""),
                            arguments.get("message", ""),
                            arguments.get("recipient")
                        )
                    else:
                        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
                    
                    return {"result": result, "tool": tool_name}
                    
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
    
    def setup_mcp_tools(self):
        """Setup MCP tools for LLM access."""
        if not MCP_AVAILABLE or not MCP_TOOLS_AVAILABLE:
            return
            
        # PR Analysis Tools
        @self.mcp.tool()
        async def analyze_file_changes(base_branch: str = "main", include_diff: bool = True, max_diff_lines: int = 500) -> str:
            """Analyze git file changes."""
            try:
                import subprocess
                result = subprocess.run(
                    ["git", "diff", "--stat", f"{base_branch}...HEAD"],
                    capture_output=True, text=True
                )
                return json.dumps({
                    "stats": result.stdout,
                    "base_branch": base_branch,
                    "include_diff": include_diff
                })
            except Exception as e:
                return json.dumps({"error": str(e)})
        
        @self.mcp.tool()
        async def get_pr_templates() -> str:
            """Get available PR templates."""
            templates = [
                {"name": "bug.md", "type": "Bug Fix"},
                {"name": "feature.md", "type": "Feature"},
                {"name": "docs.md", "type": "Documentation"},
                {"name": "refactor.md", "type": "Refactor"},
                {"name": "test.md", "type": "Test"},
                {"name": "performance.md", "type": "Performance"},
                {"name": "security.md", "type": "Security"}
            ]
            return json.dumps(templates)
        
        @self.mcp.tool()
        async def suggest_template(changes_summary: str, change_type: str) -> str:
            """Suggest appropriate PR template based on changes."""
            templates_response = await self.get_pr_templates()
            templates = json.loads(templates_response)
            
            type_mapping = {
                "bug": "bug.md", "fix": "bug.md",
                "feature": "feature.md", "enhancement": "feature.md",
                "docs": "docs.md", "documentation": "docs.md",
                "refactor": "refactor.md", "cleanup": "refactor.md",
                "test": "test.md", "testing": "test.md",
                "performance": "performance.md", "optimization": "performance.md",
                "security": "security.md"
            }
            
            template_file = type_mapping.get(change_type.lower(), "feature.md")
            selected_template = next((t for t in templates if t["name"] == template_file), templates[0])
            
            return json.dumps({
                "recommended_template": selected_template,
                "reasoning": f"Based on your analysis: '{changes_summary}', this appears to be a {change_type} change.",
                "template_content": selected_template["content"],
                "usage_hint": "Claude can help you fill out this template."
            }, indent=2)
        
        # CI Monitoring Tools
        @self.mcp.tool()
        async def get_recent_actions_events(limit: int = 10) -> str:
            """Get recent GitHub Actions events."""
            if not EVENTS_FILE.exists():
                return json.dumps([])
            with open(EVENTS_FILE, 'r') as f:
                events = json.load(f)
            return json.dumps(events[-limit:], indent=2)
        
        @self.mcp.tool()
        async def get_workflow_status(workflow_name: str = None) -> str:
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
                        "html_url": run["html_url"]
                    }

            return json.dumps(list(workflows.values()), indent=2)
        
        @self.mcp.tool()
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
                        "html_url": run["html_url"]
                    }

            return json.dumps(list(workflows.values()), indent=2)
        
        @self.mcp.tool()
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
                        "html_url": run["html_url"]
                    }

            return json.dumps(list(workflows.values()), indent=2)
        
        # Notification Tools
        @self.mcp.tool()
        async def send_slack_notification(message: str) -> str:
            """Send Slack notification."""
            return await self.send_slack_message(message)
        
        @self.mcp.tool()
        async def send_gmail_notification(subject: str, message: str, recipient: str = None) -> str:
            """Send Gmail notification."""
            return send_gmail_notification(subject, message, recipient)
    
    async def store_event(self, event_type: str, data: dict):
        """Store GitHub event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        events = []
        if EVENTS_FILE.exists():
            with open(EVENTS_FILE, 'r') as f:
                events = json.load(f)
        
        events.append(event)
        events = events[-100:]  # Keep last 100 events
        
        with open(EVENTS_FILE, 'w') as f:
            json.dump(events, f, indent=2)
    
    async def process_event_notifications(self, event_type: str, data: dict):
        """Process event and send notifications."""
        if event_type == "push":
            repo = data.get("repository", {}).get("full_name", "Unknown")
            pusher = data.get("pusher", {}).get("name", "Unknown")
            ref = data.get("ref", "Unknown")
            
            message = f"New push to {repo} by {pusher} on {ref}"
            await self.send_slack_message(message)
            
        elif event_type == "workflow_run":
            workflow = data.get("workflow_run", {})
            workflow_name = workflow.get("name", "Unknown")
            conclusion = workflow.get("conclusion")
            repo = data.get("repository", {}).get("full_name", "Unknown")
            
            if conclusion == "failure":
                message = f"CI Failure Alert - Workflow: {workflow_name}, Repository: {repo}, Branch: {workflow.get('head_branch', 'Unknown')}, Run Number: {workflow.get('run_number', 'Unknown')}, View Details: {workflow.get('html_url', '#')}"
                await self.send_slack_message(message)
                
            elif conclusion == "success":
                message = f"Deployment Successful - Workflow: {workflow_name}, Repository: {repo}, Branch: {workflow.get('head_branch', 'Unknown')}, Run Number: {workflow.get('run_number', 'Unknown')}, View Details: {workflow.get('html_url', '#')}"
                await self.send_slack_message(message)
    
    async def send_slack_message(self, message: str) -> str:
        """Send message to Slack."""
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not webhook_url:
            return "Error: SLACK_WEBHOOK_URL not set"
        
        try:
            payload = {"text": message, "mrkdwn": True}
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                return "Slack message sent successfully"
            else:
                return f"Slack error: {response.status_code}"
        except Exception as e:
            return f"Slack error: {str(e)}"
    
    async def send_gmail_message(self, subject: str, message: str, recipient: str = None) -> str:
        """Send message via Gmail."""
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        default_recipient = os.getenv("DEFAULT_EMAIL_RECIPIENT")
        
        if not gmail_user or not gmail_password:
            return "Error: GMAIL_USER and GMAIL_APP_PASSWORD not set"
        
        recipient = recipient or default_recipient
        if not recipient:
            return "Error: No recipient email specified"
        
        try:
            msg = MIMEMultipart()
            msg['From'] = gmail_user
            msg['To'] = recipient
            msg['Subject'] = subject
            
            html_body = f"""
            <html>
            <body>
                <h2>{subject}</h2>
                <div style="font-family: Arial, sans-serif; line-height: 1.6;">
                    {message.replace(chr(10), '<br>')}
                </div>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    Sent by MCP-AutoPRX Unified Server
                </p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_user, gmail_password)
            text = msg.as_string()
            server.sendmail(gmail_user, recipient, text)
            server.quit()
            
            return f"Gmail sent successfully to {recipient}"
            
        except Exception as e:
            return f"Gmail error: {str(e)}"
    
    def run(self):
        """Run the unified server."""
        port = int(os.getenv("PORT", 8080))
        
        print("Starting MCP-AutoPRX Unified Server...")
        print(f"Server will be available at: http://0.0.0.0:{port}")
        print("Combined services:")
        print("  - GitHub webhook handling")
        print("  - MCP server for LLMs")
        print("  - Slack and Gmail notifications")
        print("Available endpoints:")
        print("  - / (server info)")
        print("  - /health (health check)")
        print("  - /tools (list available tools)")
        print("  - /webhook/github (GitHub webhooks)")
        print("  - /mcp (MCP endpoint)")
        print("  - /call/{tool_name} (direct tool calling)")
        print("  - /docs (API documentation)")
        print()
        
        if not FASTAPI_AVAILABLE:
            print("FastAPI not available. Install with: pip install fastapi uvicorn")
            return
        
        uvicorn.run(self.app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    server = UnifiedServer()
    server.run() 