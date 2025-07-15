# === File: prompts/ci_prompts.py ===

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_instance import mcp

@mcp.tool()
async def format_ci_failure_alert():
    return """Format this GitHub Actions failure as a Slack message using ONLY Slack markdown syntax:

:rotating_light: *CI Failure Alert* :rotating_light:

A CI workflow has failed:
*Workflow*: workflow_name
*Description*: workflow_description
*Branch*: branch_name
*Status*: Failed
*Run Number*: run_number
*View Details*: <workflow_url|View Logs>

Please check the logs and address any issues.

For documentation workflows:
- Check if it's a build or upload issue
- Verify Hugging Face tokens are valid
- Check documentation syntax

Slack formatting rules:
- *text* for bold (NOT **text**)
- `text` for code
- > text for quotes
- Use simple bullet format
- :emoji_name: for emojis"""

@mcp.tool()
async def format_ci_success_summary():
    return """Format this successful GitHub Actions run as a Slack message using ONLY Slack markdown syntax:

:white_check_mark: *Deployment Successful* :white_check_mark:

Deployment completed successfully for [Repository Name]

*Changes:*
- Key feature or fix 1
- Key feature or fix 2

*Links:*
<https://github.com/user/repo|View Changes>

Slack formatting rules:
- *text* for bold (NOT **text**)
- `text` for code
- > text for quotes
- Use simple bullet format
- :emoji_name: for emojis"""