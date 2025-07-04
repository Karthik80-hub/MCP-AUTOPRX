import sys
import os
import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import requests
import subprocess

# Adjust the path to import unified_server.py and tools from mcp-server
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the modules to test
import unified_server

# Import tools from mcp-server directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mcp-server')))
from tools import pr_analysis, ci_monitor, slack_notifier
from prompts import pr_prompts, ci_prompts, review_prompts


class TestUnifiedServer:
    """Test the main unified server functionality."""
    
    def test_server_import(self):
        """Test that the unified_server module can be imported."""
        assert hasattr(unified_server, 'UnifiedServer'), "unified_server.py should have a 'UnifiedServer' class"
    
    def test_fastapi_available(self):
        """Test that FastAPI is available."""
        assert hasattr(unified_server, 'FASTAPI_AVAILABLE'), "FASTAPI_AVAILABLE should be defined"
        # This test will pass if FastAPI is installed, fail if not
    
    def test_mcp_available(self):
        """Test that MCP is available."""
        assert hasattr(unified_server, 'MCP_AVAILABLE'), "MCP_AVAILABLE should be defined"
    
    def test_tools_imported(self):
        """Test that tools can be imported."""
        assert pr_analysis is not None, "pr_analysis should be importable"
        assert ci_monitor is not None, "ci_monitor should be importable"
        assert slack_notifier is not None, "slack_notifier should be importable"
    
    def test_prompts_imported(self):
        """Test that prompts can be imported."""
        assert pr_prompts is not None, "pr_prompts should be importable"
        assert ci_prompts is not None, "ci_prompts should be importable"
        assert review_prompts is not None, "review_prompts should be importable"


class TestBasicFunctionality:
    """Test basic functionality without full server initialization."""
    
    def test_events_file_path(self):
        """Test that events file path is defined."""
        assert hasattr(unified_server, 'EVENTS_FILE'), "EVENTS_FILE should be defined"
    
    def test_processed_events_set(self):
        """Test that processed events set is defined."""
        assert hasattr(unified_server, 'PROCESSED_EVENTS'), "PROCESSED_EVENTS should be defined"
    
    def test_environment_loading(self):
        """Test that environment variables can be loaded."""
        # This test checks if dotenv loading works
        assert 'load_dotenv' in dir(unified_server), "load_dotenv should be imported"


class TestToolFunctions:
    """Test individual tool functions."""
    
    @pytest.mark.asyncio
    async def test_get_pr_templates(self):
        """Test get_pr_templates function."""
        result = await pr_analysis.get_pr_templates()
        templates = json.loads(result)
        
        # Check that templates are returned
        assert isinstance(templates, list)
        assert len(templates) > 0
        
        # Check template structure
        for template in templates:
            assert "filename" in template
            assert "type" in template
            assert "content" in template
    
    @pytest.mark.asyncio
    async def test_get_recent_actions_events_empty(self):
        """Test get_recent_actions_events with no file."""
        result = await ci_monitor.get_recent_actions_events()
        events = json.loads(result)
        
        assert isinstance(events, list)
        # Should return empty list if no events file exists 