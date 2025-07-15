# === File: mcp_server/prompts/pr_prompts.py ===

import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_instance import mcp
from tools.pr_analysis import get_pr_templates

TYPE_MAPPING = {
    "bug": "bug.md",
    "fix": "bug.md",
    "feature": "feature.md",
    "enhancement": "feature.md",
    "docs": "docs.md",
    "documentation": "docs.md",
    "refactor": "refactor.md",
    "cleanup": "refactor.md",
    "test": "test.md",
    "testing": "test.md",
    "performance": "performance.md",
    "optimization": "performance.md",
    "security": "security.md"
}

@mcp.tool()
async def suggest_template(changes_summary: str, change_type: str) -> str:
    templates_response = await get_pr_templates()
    templates = json.loads(templates_response)
    template_file = TYPE_MAPPING.get(change_type.lower(), "feature.md")
    selected_template = next((t for t in templates if t["filename"] == template_file), templates[0])
    return json.dumps({
        "recommended_template": selected_template,
        "reasoning": f"Based on your analysis: '{changes_summary}', this appears to be a {change_type} change.",
        "template_content": selected_template["content"],
        "usage_hint": "Claude can help you fill out this template."
    }, indent=2)
