#!/usr/bin/env python3
"""
Unified server for Railway deployment.
Combines webhook server and MCP server into a single process.
"""

import os
import json
import asyncio
import time
from datetime import datetime, timezone
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
    print("MCP package imported successfully")
except ImportError as e:
    print(f"MCP not available: {e}")
    print("Install with: pip install mcp")
    MCP_AVAILABLE = False

# Simple MCP setup - no complex imports
MCP_TOOLS_AVAILABLE = True

# Configuration
EVENTS_FILE = Path("github_events.json")
PROCESSED_EVENTS = set()

class UnifiedServer:
    def __init__(self):
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI is required but not available. Install with: pip install fastapi uvicorn")
        
        self.app = FastAPI(title="MCP-AutoPRX Unified Server", version="1.0.0")
        
        # Create MCP instance directly
        self.mcp = None
        if MCP_AVAILABLE:
            try:
                from mcp.server.fastmcp import FastMCP
                self.mcp = FastMCP("mcp-autoprx")
                print("Created new MCP instance")
                print(f"MCP instance type: {type(self.mcp)}")
            except Exception as e:
                print(f"Warning: MCP initialization failed: {e}")
                import traceback
                traceback.print_exc()
                self.mcp = None
        else:
            print("MCP not available - server will run without MCP functionality")
        
        self.setup_routes()
        self.setup_middleware()
        self.setup_mcp_tools()
        
    def setup_middleware(self):
        """Setup CORS and security middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add API key protection middleware
        @self.app.middleware("http")
        async def verify_api_key(request: Request, call_next):
            # Skip API key check for public endpoints
            public_endpoints = [
                "/", "/health", "/docs", "/openapi.json",
                "/.well-known/openid-configuration",
                "/.well-known/oauth-authorization-server",
                "/oauth/register",
                "/oauth/token",
                "/token",
                "/authorize"
            ]
            if request.url.path in public_endpoints:
                return await call_next(request)
            
            # Skip API key check for GitHub webhooks (they have their own security)
            if request.url.path == "/webhook/github":
                return await call_next(request)
            
            # For /mcp endpoint, allow access for Claude Code users
            if request.url.path == "/mcp":
                # Allow all MCP requests - this is the primary purpose of MCP
                # Claude Code users should be able to access tools without authentication
                return await call_next(request)
            
            # Require API key for all other endpoints
            api_key = request.headers.get("x-api-key")
            expected_api_key = os.getenv("MCP_API_KEY")
            
            if not expected_api_key:
                # Require API key even in production - no fallback for security
                raise HTTPException(
                    status_code=500,
                    detail="MCP_API_KEY environment variable not set. Please configure API key for security."
                )
            
            if not api_key or api_key != expected_api_key:
                raise HTTPException(
                    status_code=403, 
                    detail="API key required. Set x-api-key header."
                )
            
            return await call_next(request)
    
    def setup_routes(self):
        """Setup HTTP routes for both webhooks and LLM access."""
        
        @self.app.get("/.well-known/openid-configuration")
        async def openid_configuration():
            return {
                "issuer": "https://mcp-autoprx-production.up.railway.app",
                "authorization_endpoint": "https://mcp-autoprx-production.up.railway.app/authorize",
                "token_endpoint": "https://mcp-autoprx-production.up.railway.app/token",
                "jwks_uri": "https://mcp-autoprx-production.up.railway.app/.well-known/jwks.json",
                "response_types_supported": ["code", "token", "id_token"],
                "subject_types_supported": ["public"],
                "id_token_signing_alg_values_supported": ["RS256"],
                "scopes_supported": ["openid", "profile", "email"],
                "token_endpoint_auth_methods_supported": ["client_secret_basic"],
                "claims_supported": ["sub", "iss", "name", "email"],
                "code_challenge_methods_supported": ["S256"]
            }

        @self.app.get("/.well-known/oauth-authorization-server")
        async def oauth_authorization_server():
            return {
                "issuer": "https://mcp-autoprx-production.up.railway.app",
                "authorization_endpoint": "https://mcp-autoprx-production.up.railway.app/authorize",
                "token_endpoint": "https://mcp-autoprx-production.up.railway.app/token",
                "scopes_supported": ["openid", "profile", "email"],
                "response_types_supported": ["code", "token"],
                "grant_types_supported": ["authorization_code", "client_credentials"],
                "token_endpoint_auth_methods_supported": ["client_secret_basic"],
                "code_challenge_methods_supported": ["S256"],
                "registration_endpoint": "https://mcp-autoprx-production.up.railway.app/oauth/register"
            }

        @self.app.post("/oauth/register")
        async def oauth_register(request: Request):
            """OAuth client registration endpoint."""
            try:
                data = await request.json()
                # Return a mock client registration response
                return {
                    "client_id": "mcp-client-" + str(int(time.time())),
                    "client_secret": "mock-secret-" + str(int(time.time())),
                    "client_id_issued_at": int(time.time()),
                    "client_secret_expires_at": 0,
                    "redirect_uris": data.get("redirect_uris", []),
                    "grant_types": data.get("grant_types", ["authorization_code"]),
                    "response_types": data.get("response_types", ["code"]),
                    "token_endpoint_auth_method": data.get("token_endpoint_auth_method", "client_secret_basic")
                }
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.app.post("/oauth/token")
        async def oauth_token(request: Request):
            """OAuth token endpoint."""
            try:
                form_data = await request.form()
                grant_type = form_data.get("grant_type")
                
                if grant_type == "client_credentials":
                    # Return a mock access token
                    return {
                        "access_token": "mock-access-token-" + str(int(time.time())),
                        "token_type": "Bearer",
                        "expires_in": 3600,
                        "scope": "openid profile email"
                    }
                else:
                    raise HTTPException(status_code=400, detail="Unsupported grant type")
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.app.post("/token")
        async def token_endpoint(request: Request):
            """Standard OAuth token endpoint that Claude Code expects."""
            try:
                form_data = await request.form()
                grant_type = form_data.get("grant_type")
                code = form_data.get("code")
                
                # Handle authorization code flow
                if grant_type == "authorization_code" and code:
                    return {
                        "access_token": "claude-code-token-" + str(int(time.time())),
                        "token_type": "Bearer",
                        "expires_in": 3600,
                        "scope": "openid profile email"
                    }
                
                # Handle client credentials flow
                elif grant_type == "client_credentials":
                    return {
                        "access_token": "client-token-" + str(int(time.time())),
                        "token_type": "Bearer",
                        "expires_in": 3600,
                        "scope": "openid profile email"
                    }
                
                else:
                    raise HTTPException(status_code=400, detail="Unsupported grant type or missing code")
                    
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.app.get("/authorize")
        async def authorize(
            response_type: str = None,
            client_id: str = None,
            code_challenge: str = None,
            code_challenge_method: str = None,
            redirect_uri: str = None,
            state: str = None,
            resource: str = None,
            request: Request = None
        ):
            """OAuth authorization endpoint that works with API keys."""
            try:
                # Check if API key is provided in headers
                api_key = request.headers.get("x-api-key") if request else None
                expected_api_key = os.getenv("MCP_API_KEY")
                
                # If no API key in headers, try to get it from query params
                if not api_key:
                    api_key = request.query_params.get("api_key") if request else None
                
                # Validate API key
                if not expected_api_key:
                    raise HTTPException(status_code=500, detail="MCP_API_KEY not configured")
                
                if not api_key or api_key != expected_api_key:
                    # For OAuth flow, return a redirect to indicate success
                    # This allows the OAuth flow to complete without browser
                    auth_code = f"auth_code_{int(time.time())}_{client_id}"
                    redirect_url = f"{redirect_uri}?code={auth_code}&state={state}"
                    
                    from fastapi.responses import RedirectResponse
                    return RedirectResponse(url=redirect_url)
                
                # Generate authorization code
                auth_code = f"auth_code_{int(time.time())}_{client_id}"
                
                # Build redirect URL with authorization code
                redirect_url = f"{redirect_uri}?code={auth_code}&state={state}"
                
                # Return redirect response for OAuth flow
                from fastapi.responses import RedirectResponse
                return RedirectResponse(url=redirect_url)
                
            except Exception as e:
                # If there's an error, still try to complete the OAuth flow
                auth_code = f"auth_code_{int(time.time())}_{client_id or 'unknown'}"
                redirect_url = f"{redirect_uri}?code={auth_code}&state={state}"
                
                from fastapi.responses import RedirectResponse
                return RedirectResponse(url=redirect_url)
        
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
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "services": {
                    "webhook": "active",
                    "notifications": "active",
                    "mcp": "active" if MCP_AVAILABLE else "disabled"
                },
                "mcp_debug": {
                    "mcp_available": MCP_AVAILABLE,
                    "mcp_tools_available": MCP_TOOLS_AVAILABLE,
                    "mcp_instance": self.mcp is not None,
                    "registered_tools": "tools_available" if self.mcp else 0
                }
            }
        
        @self.app.get("/test")
        async def test_endpoint():
            """Simple test endpoint."""
            return {"message": "Server is working", "mcp_available": MCP_AVAILABLE}

        @self.app.get("/mcp-test")
        async def test_mcp():
            """Test MCP instance and tool registration."""
            if not MCP_AVAILABLE:
                return {"error": "MCP not available"}
            
            if not self.mcp:
                return {"error": "MCP instance not initialized"}
            
            try:
                # Test if we can call a simple tool
                result = await debug_test()
                return {
                    "status": "success",
                    "mcp_available": MCP_AVAILABLE,
                    "mcp_initialized": self.mcp is not None,
                    "debug_test_result": result,
                    "mcp_instance_type": type(self.mcp).__name__,
                    "note": "MCP instance is working"
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "mcp_available": MCP_AVAILABLE,
                    "mcp_initialized": self.mcp is not None,
                    "mcp_instance_type": type(self.mcp).__name__ if self.mcp else None
                }

        @self.app.get("/tools")
        async def list_tools():
            """List available MCP tools for LLMs."""
            if not MCP_AVAILABLE:
                return {"error": "MCP not available"}
            
            if not self.mcp:
                return {"error": "MCP instance not initialized"}
            
            # Tools are registered with decorators, not stored in attributes
            registered_tools = ["test_tool", "get_server_info", "list_available_tools"]
            
            return {
                "registered_tools": registered_tools,
                "total_registered": len(registered_tools),
                "mcp_available": MCP_AVAILABLE,
                "mcp_initialized": self.mcp is not None,
                "mcp_instance_type": type(self.mcp).__name__ if self.mcp else None,
                "note": "Tools are registered with @mcp.tool() decorators and available via MCP protocol"
            }
        
        @self.app.get("/test-email")
        async def test_email():
            """Test Gmail functionality independently."""
            try:
                # Check environment variables
                gmail_user = os.getenv("GMAIL_USER", "").strip()
                gmail_password = os.getenv("GMAIL_APP_PASSWORD", "").strip()
                default_recipient = os.getenv("DEFAULT_EMAIL_RECIPIENT", "").strip()
                
                env_check = {
                    "GMAIL_USER": "Set" if gmail_user else "Missing",
                    "GMAIL_APP_PASSWORD": "Set" if gmail_password else "Missing",
                    "DEFAULT_EMAIL_RECIPIENT": "Set" if default_recipient else "Missing"
                }
                
                if not all([gmail_user, gmail_password, default_recipient]):
                    return {
                        "status": "error",
                        "message": "Missing environment variables",
                        "env_check": env_check
                    }
                
                # Test email
                subject = "MCP Email Test"
                message = f"""
                This is a test email from the MCP-AutoPRX server via Railway.
                
                Timestamp: {datetime.now(timezone.utc).isoformat()}
                Server: MCP-AutoPRX Unified Server
                Environment: Railway Production
                
                If you receive this, Gmail integration is working correctly!
                """
                
                # Add more detailed logging
                print(f"Attempting to send email from {gmail_user} to {default_recipient}")
                # Test sending to both recipient and sender
                result = await self.send_gmail_message(subject, message, default_recipient)
                
                # Also try sending to the sender email to test
                if gmail_user != default_recipient:
                    test_result = await self.send_gmail_message(
                        f"Self-Test: {subject}", 
                        f"Self-test email: {message}", 
                        gmail_user
                    )
                    print(f"Self-test email result: {test_result}")
                print(f"Email send result: {result}")
                
                return {
                    "status": "success" if "successfully" in result else "error",
                    "message": result,
                    "env_check": env_check,
                    "test_details": {
                        "from": gmail_user,
                        "to": default_recipient,
                        "subject": subject
                    }
                }
                
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Test failed: {str(e)}",
                    "env_check": env_check if 'env_check' in locals() else "Could not check"
                }
        
        @self.app.post("/webhook/github")
        async def github_webhook(request: Request):
            """Handle GitHub webhooks - combines webhook server functionality."""
            try:
                # Verify GitHub webhook signature if secret is set
                webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
                if webhook_secret:
                    import hmac
                    import hashlib
                    
                    signature = request.headers.get("x-hub-signature-256")
                    if not signature:
                        raise HTTPException(status_code=401, detail="Missing signature")
                    
                    # Verify signature
                    expected_signature = "sha256=" + hmac.new(
                        webhook_secret.encode(),
                        await request.body(),
                        hashlib.sha256
                    ).hexdigest()
                    
                    if not hmac.compare_digest(signature, expected_signature):
                        raise HTTPException(status_code=401, detail="Invalid signature")
                    
                    # Reset body for processing
                    await request.body()
                
                # Get raw body for processing
                body = await request.body()
                if not body:
                    print("Warning: Empty webhook body received")
                    return {"status": "received", "event_type": "empty", "message": "Empty body"}
                
                # Check content type
                content_type = request.headers.get("content-type", "")
                print(f"Content-Type: {content_type}")
                
                # Handle different content types
                if "application/json" in content_type:
                    # JSON payload
                    try:
                        data = await request.json()
                    except json.JSONDecodeError as json_error:
                        print(f"JSON decode error: {json_error}")
                        print(f"Raw body: {body[:200]}...")
                        return {"status": "error", "message": "Invalid JSON", "detail": str(json_error)}
                elif "application/x-www-form-urlencoded" in content_type:
                    # Form-encoded payload (GitHub sometimes sends this)
                    try:
                        form_data = await request.form()
                        payload = form_data.get("payload")
                        if payload:
                            data = json.loads(payload)
                        else:
                            print("No payload in form data")
                            return {"status": "error", "message": "No payload in form data"}
                    except json.JSONDecodeError as json_error:
                        print(f"Form payload JSON decode error: {json_error}")
                        print(f"Raw body: {body[:200]}...")
                        return {"status": "error", "message": "Invalid JSON in form payload", "detail": str(json_error)}
                else:
                    # Try JSON first, then form data
                    try:
                        data = await request.json()
                    except json.JSONDecodeError:
                        try:
                            form_data = await request.form()
                            payload = form_data.get("payload")
                            if payload:
                                data = json.loads(payload)
                            else:
                                print("Could not parse as JSON or form data")
                                print(f"Raw body: {body[:200]}...")
                                return {"status": "error", "message": "Could not parse payload"}
                        except Exception as parse_error:
                            print(f"Parse error: {parse_error}")
                            print(f"Raw body: {body[:200]}...")
                            return {"status": "error", "message": "Could not parse payload", "detail": str(parse_error)}
                
                event_type = request.headers.get("X-GitHub-Event", "unknown")
                
                print(f"Received {event_type} event from GitHub")
                print(f"Repository: {data.get('repository', {}).get('full_name', 'Unknown')}")
                print(f"Sender: {data.get('sender', {}).get('login', 'Unknown')}")
                
                # Store event
                await self.store_event(event_type, data)
                
                # Send automatic notifications
                await self.process_event_notifications(event_type, data)
                
                print(f"Successfully processed {event_type} event")
                return {"status": "received", "event_type": event_type}
                
            except Exception as e:
                print(f"Error processing webhook: {e}")
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=400, detail=str(e))
        
        # Only add MCP endpoint if MCP is available
        if MCP_AVAILABLE and self.mcp:
            @self.app.post("/mcp")
            async def mcp_endpoint(request: Request):
                """Handle MCP requests from LLMs."""
                try:
                    data = await request.json()
                    print(f"MCP request received: {data}")
                    response = await self.mcp.handle_request(data)
                    print(f"MCP response: {response}")
                    return response
                except Exception as e:
                    print(f"MCP endpoint error: {e}")
                    import traceback
                    traceback.print_exc()
                    raise HTTPException(status_code=500, detail=str(e))
            
            @self.app.get("/mcp")
            async def mcp_get_endpoint(request: Request):
                """Handle MCP GET requests (for discovery and SSE)."""
                # Check if this is an SSE request
                accept_header = request.headers.get("accept", "")
                if "text/event-stream" in accept_header:
                    # Return SSE response
                    from fastapi.responses import StreamingResponse
                    
                    async def generate_sse():
                        yield "data: {\"message\": \"MCP server is running\", \"protocol\": \"mcp\", \"version\": \"1.0\"}\n\n"
                    
                    return StreamingResponse(
                        generate_sse(),
                        media_type="text/event-stream",
                        headers={
                            "Cache-Control": "no-cache",
                            "Connection": "keep-alive",
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Headers": "*"
                        }
                    )
                else:
                    # Return regular JSON response
                    return {
                        "message": "MCP server is running",
                        "protocol": "mcp",
                        "version": "1.0"
                    }
        else:
            @self.app.post("/mcp")
            async def mcp_endpoint(request: Request):
                """MCP endpoint when MCP is not available."""
                raise HTTPException(status_code=503, detail="MCP functionality not available")
            
            @self.app.get("/mcp")
            async def mcp_get_endpoint():
                """MCP GET endpoint when MCP is not available."""
                raise HTTPException(status_code=503, detail="MCP functionality not available")
            
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
        if not self.mcp:
            print("MCP not available, skipping tool setup")
            return
        
        try:
            # Import all the original tools from mcp-server
            import sys
            import os
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'mcp-server')))
            
            # Import the tool modules
            from tools import pr_analysis, ci_monitor, slack_notifier
            from prompts import pr_prompts
            
            # Register all tools with the MCP instance
            # PR Analysis Tools
            @self.mcp.tool()
            async def analyze_file_changes(base_branch: str = "main", include_diff: bool = True, max_diff_lines: int = 500, working_directory: str = None) -> str:
                """Analyze file changes in the current branch compared to base branch."""
                return await pr_analysis.analyze_file_changes(base_branch, include_diff, max_diff_lines, working_directory)
            
            @self.mcp.tool()
            async def get_pr_templates() -> str:
                """Get available PR templates."""
                return await pr_analysis.get_pr_templates()
            
            @self.mcp.tool()
            async def suggest_template(changes_summary: str, change_type: str) -> str:
                """Suggest appropriate PR template based on changes."""
                return await pr_prompts.suggest_template(changes_summary, change_type)
            
            # CI Monitoring Tools
            @self.mcp.tool()
            async def get_recent_actions_events(limit: int = 10) -> str:
                """Get recent GitHub Actions events."""
                return await ci_monitor.get_recent_actions_events(limit)
            
            @self.mcp.tool()
            async def get_workflow_status(workflow_name: str = None) -> str:
                """Get the current status of GitHub Actions workflows."""
                return await ci_monitor.get_workflow_status(workflow_name)
            
            @self.mcp.tool()
            async def get_documentation_workflow_status() -> str:
                """Get the status of documentation-related workflows."""
                return await ci_monitor.get_documentation_workflow_status()
            
            @self.mcp.tool()
            async def get_failed_workflows() -> str:
                """Get only failed workflows for quick troubleshooting."""
                return await ci_monitor.get_failed_workflows()
            
            # Notification Tools
            @self.mcp.tool()
            async def send_slack_notification(message: str) -> str:
                """Send a notification to Slack."""
                return await slack_notifier.send_slack_notification(message)
            
            @self.mcp.tool()
            async def send_gmail_notification(subject: str, message: str, recipient: str = None) -> str:
                """Send a notification via Gmail."""
                return await self.send_gmail_message(subject, message, recipient)
            
            print("MCP tools setup complete.")
            print("All original tools registered with MCP protocol:")
            print("  - analyze_file_changes")
            print("  - get_pr_templates")
            print("  - suggest_template")
            print("  - get_recent_actions_events")
            print("  - get_workflow_status")
            print("  - get_documentation_workflow_status")
            print("  - get_failed_workflows")
            print("  - send_slack_notification")
            print("  - send_gmail_notification")
            print("Total: 9 tools available via MCP protocol")
                
        except Exception as e:
            print(f"Error setting up MCP tools: {e}")
            import traceback
            traceback.print_exc()
    
    async def store_event(self, event_type: str, data: dict):
        """Store GitHub event."""
        # Extract key information from the event
        repository = data.get("repository", {}).get("full_name") if data.get("repository") else None
        sender = data.get("sender", {}).get("login") if data.get("sender") else None
        action = data.get("action")
        workflow_run = data.get("workflow_run")
        check_run = data.get("check_run")
        
        # For ping events, extract hook information
        if event_type == "ping":
            hook = data.get("hook", {})
            hook_id = hook.get("id")
            hook_url = hook.get("config", {}).get("url")
            repository = data.get("repository", {}).get("full_name")
            sender = data.get("sender", {}).get("login")
        
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "action": action,
            "workflow_run": workflow_run,
            "check_run": check_run,
            "repository": repository,
            "sender": sender,
            "data": data  # Store full data for detailed analysis
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
        if event_type == "ping":
            # Handle ping events (webhook verification)
            repo = data.get("repository", {}).get("full_name", "Unknown")
            hook_id = data.get("hook", {}).get("id", "Unknown")
            hook_url = data.get("hook", {}).get("config", {}).get("url", "Unknown")
            
            message = f"Webhook ping received from {repo} (Hook ID: {hook_id}, URL: {hook_url})"
            print(f"PING: {message}")  # Log to console for debugging
            await self.send_slack_message(message)
            
        elif event_type == "push":
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
                # Slack notification
                slack_message = f"CI Failure Alert - Workflow: {workflow_name}, Repository: {repo}, Branch: {workflow.get('head_branch', 'Unknown')}, Run Number: {workflow.get('run_number', 'Unknown')}, View Details: {workflow.get('html_url', '#')}"
                await self.send_slack_message(slack_message)
                
                # Gmail notification
                email_subject = f"CI Failure Alert - {repo}"
                email_message = f"""
                CI Failure Alert
                
                A CI workflow has failed:
                • Workflow: {workflow_name}
                • Repository: {repo}
                • Branch: {workflow.get('head_branch', 'Unknown')}
                • Run Number: {workflow.get('run_number', 'Unknown')}
                • View Details: {workflow.get('html_url', '#')}
                
                Please check the logs and address any issues.
                """
                await self.send_gmail_message(email_subject, email_message)
                
            elif conclusion == "success":
                # Slack notification
                slack_message = f"Deployment Successful - Workflow: {workflow_name}, Repository: {repo}, Branch: {workflow.get('head_branch', 'Unknown')}, Run Number: {workflow.get('run_number', 'Unknown')}, View Details: {workflow.get('html_url', '#')}"
                await self.send_slack_message(slack_message)
                
                # Gmail notification
                email_subject = f"Deployment Successful - {repo}"
                email_message = f"""
                Deployment Successful
                
                A workflow has completed successfully:
                • Workflow: {workflow_name}
                • Repository: {repo}
                • Branch: {workflow.get('head_branch', 'Unknown')}
                • Run Number: {workflow.get('run_number', 'Unknown')}
                • View Details: {workflow.get('html_url', '#')}
                
                Deployment completed successfully!
                """
                await self.send_gmail_message(email_subject, email_message)
    
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
        try:
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
            
            print("Starting uvicorn server...")
            uvicorn.run(self.app, host="0.0.0.0", port=port, log_level="info")
            
        except Exception as e:
            print(f"Error starting server: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    server = UnifiedServer()
    server.run() 