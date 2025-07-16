# === File: mcp_server/tools/pr_analysis.py ===

import os
import json
import subprocess
from typing import Optional
from pathlib import Path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_instance import mcp

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"
DEFAULT_TEMPLATES = {
    "bug.md": "Bug Fix",
    "feature.md": "Feature",
    "docs.md": "Documentation",
    "refactor.md": "Refactor",
    "test.md": "Test",
    "performance.md": "Performance",
    "security.md": "Security"
}

@mcp.tool()
async def analyze_file_changes(base_branch: str = "main", include_diff: bool = True, max_diff_lines: int = 500, working_directory: Optional[str] = None) -> str:
    try:
        cwd = working_directory or os.getcwd()

        # Check if we're in a git repository
        try:
            subprocess.run(["git", "status"], capture_output=True, text=True, check=True, cwd=cwd)
        except subprocess.CalledProcessError:
            return json.dumps({"error": "Not in a git repository or git not available"})

        files_result = subprocess.run(["git", "diff", "--name-status", f"{base_branch}...HEAD"], capture_output=True, text=True, check=True, cwd=cwd)
        stat_result = subprocess.run(["git", "diff", "--stat", f"{base_branch}...HEAD"], capture_output=True, text=True, cwd=cwd)

        diff_content = ""
        truncated = False
        total_diff_lines = 0
        
        if include_diff:
            diff_result = subprocess.run(["git", "diff", f"{base_branch}...HEAD"], capture_output=True, text=True, cwd=cwd)
            diff_lines = diff_result.stdout.split('\n')
            total_diff_lines = len(diff_lines)
            if len(diff_lines) > max_diff_lines:
                diff_content = '\n'.join(diff_lines[:max_diff_lines]) + f"\n\n... Output truncated. Showing {max_diff_lines} of {len(diff_lines)} lines ..."
                truncated = True
            else:
                diff_content = diff_result.stdout

        commits_result = subprocess.run(["git", "log", "--oneline", f"{base_branch}..HEAD"], capture_output=True, text=True, cwd=cwd)

        return json.dumps({
            "base_branch": base_branch,
            "files_changed": files_result.stdout,
            "statistics": stat_result.stdout,
            "commits": commits_result.stdout,
            "diff": diff_content if include_diff else "Diff not included",
            "truncated": truncated,
            "total_diff_lines": total_diff_lines
        }, indent=2)

    except subprocess.CalledProcessError as e:
        return json.dumps({"error": f"Git error: {e.stderr}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_pr_templates() -> str:
    templates = []
    for filename, template_type in DEFAULT_TEMPLATES.items():
        template_path = TEMPLATES_DIR / filename
        if template_path.exists():
            try:
                content = template_path.read_text()
            except Exception:
                content = f"# {template_type}\n\nTemplate content not available."
        else:
            content = f"# {template_type}\n\nTemplate file not found: {filename}"
        
        templates.append({
            "filename": filename,
            "type": template_type,
            "content": content
        })
    
    return json.dumps(templates, indent=2)
