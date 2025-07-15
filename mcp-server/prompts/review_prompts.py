# === File: prompts/review_prompts.py ===

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_instance import mcp

@mcp.tool()
async def analyze_ci_results():
    return """Please analyze the recent CI/CD results from GitHub Actions:

1. Call get_recent_actions_events()
2. Then call get_workflow_status()
3. Identify failures or issues
4. Provide next steps

Format:
## CI/CD Status Summary
- *Overall Health*: [Good/Warning/Critical]
- *Failed Workflows*: [List any failures with links]
- *Successful Workflows*: [List recent successes]
- *Recommendations*: [Actions to take]
- *Trends*: [Patterns you notice]"""

@mcp.tool()
async def create_deployment_summary():
    return """Create a deployment summary:

Deployment Update
- Status: [Success / Failed / In Progress]
- *Environment*: [Production/Staging/Dev]
- *Version/Commit*: [If available]
- *Duration*: [If available]
- *Key Changes*: [Brief summary]
- *Issues*: [Problems if any]
- *Next Steps*: [Required actions if failed]"""

@mcp.tool()
async def generate_pr_status_report():
    return """Generate a comprehensive PR status report:

## PR Status Report

### Code Changes
- *Files Modified*: [Count by type]
- *Change Type*: [Feature/Bug/Refactor/etc.]
- *Impact Assessment*: [High/Medium/Low]
- *Key Changes*: [Bullet points]

### CI/CD Status
- All Checks: [Pass/Fail/Pending]
- *Test Results*: [Pass rate, failed tests]
- *Build Status*: [Success/Failed]
- *Code Quality*: [Linting, coverage]

### 📌 Recommendations
- *PR Template*: [Suggested template]
- *Next Steps*: [Before merge]
- *Reviewers*: [Suggested reviewers]

### Risks & Considerations
- [Deployment risks]
- [Breaking changes]
- [Dependencies]"""

@mcp.tool()
async def troubleshoot_workflow_failure():
    return """Help troubleshoot GitHub Actions workflows:

## Workflow Troubleshooting Guide

### Failed Workflow Details
- *Workflow Name*: [name]
- *Failure Type*: [Test/Build/Deploy]
- *First Failed*: [Time]
- *Failure Rate*: [Intermittent/Consistent]

### Diagnostic Info
- *Error Patterns*: [Error messages]
- *Recent Changes*: [Before failure]
- *Dependencies*: [External resources]

### Possible Causes
1. *Most Likely*: [...]
2. *Likely*: [...]
3. *Possible*: [...]

### Suggested Fixes
- [ ] Immediate actions
- [ ] Investigation steps
- [ ] Long-term solutions

### Resources
- [Docs, issue links]"""
