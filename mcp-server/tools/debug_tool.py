# === File: tools/debug_tool.py ===

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_instance import mcp

@mcp.tool()
async def debug_test() -> str:
    """Simple debug tool to test if MCP tool registration is working."""
    return "Debug tool is working! MCP tool registration is successful."

@mcp.tool()
async def list_environment() -> str:
    """List environment variables to help with debugging."""
    import os
    env_vars = {k: v for k, v in os.environ.items() if not k.startswith('_')}
    return f"Environment variables: {env_vars}" 