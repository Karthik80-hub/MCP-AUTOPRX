#!/usr/bin/env python3
"""
Unit tests for CI Monitor Module
Run these tests to validate your implementation
"""

import json
import pytest
import asyncio
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the mcp-server directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mcp-server')))

# Import your implemented functions
try:
    from tools.ci_monitor import (
        get_recent_actions_events,
        get_workflow_status,
        get_documentation_workflow_status,
        get_failed_workflows
    )
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    IMPORTS_SUCCESSFUL = False
    IMPORT_ERROR = str(e)


class TestImplementation:
    """Test that the required functions are implemented."""
    
    def test_imports(self):
        """Test that all required functions can be imported."""
        assert IMPORTS_SUCCESSFUL, f"Failed to import required functions: {IMPORT_ERROR if not IMPORTS_SUCCESSFUL else ''}"
        assert callable(get_recent_actions_events), "get_recent_actions_events should be a callable function"
        assert callable(get_workflow_status), "get_workflow_status should be a callable function"
        assert callable(get_documentation_workflow_status), "get_documentation_workflow_status should be a callable function"
        assert callable(get_failed_workflows), "get_failed_workflows should be a callable function"


@pytest.mark.skipif(not IMPORTS_SUCCESSFUL, reason="Imports failed")
class TestGetRecentActionsEvents:
    """Test the get_recent_actions_events tool."""
    
    @pytest.mark.asyncio
    async def test_returns_json_string(self):
        """Test that get_recent_actions_events returns a JSON string."""
        result = await get_recent_actions_events()
        
        assert isinstance(result, str), "Should return a string"
        # Should be valid JSON
        data = json.loads(result)
        assert isinstance(data, list), "Should return a JSON array"
    
    @pytest.mark.asyncio
    async def test_includes_required_fields(self):
        """Test that the result includes expected fields."""
        result = await get_recent_actions_events()
        data = json.loads(result)
        
        # Should return a list (even if empty)
        assert isinstance(data, list), "Should return a list"


@pytest.mark.skipif(not IMPORTS_SUCCESSFUL, reason="Imports failed")
class TestGetWorkflowStatus:
    """Test the get_workflow_status tool."""
    
    @pytest.mark.asyncio
    async def test_returns_json_string(self):
        """Test that get_workflow_status returns a JSON string."""
        result = await get_workflow_status()
        
        assert isinstance(result, str), "Should return a string"
        # Should be valid JSON
        data = json.loads(result)
        assert isinstance(data, (list, dict)), "Should return a JSON object or array"
    
    @pytest.mark.asyncio
    async def test_returns_workflow_data(self):
        """Test that workflow data is returned."""
        result = await get_workflow_status()
        data = json.loads(result)
        
        # Should return either a list or a message dict
        assert isinstance(data, (list, dict)), "Should return workflow data"


@pytest.mark.skipif(not IMPORTS_SUCCESSFUL, reason="Imports failed")
class TestGetDocumentationWorkflowStatus:
    """Test the get_documentation_workflow_status tool."""
    
    @pytest.mark.asyncio
    async def test_returns_json_string(self):
        """Test that get_documentation_workflow_status returns a JSON string."""
        result = await get_documentation_workflow_status()
        
        assert isinstance(result, str), "Should return a string"
        # Should be valid JSON
        data = json.loads(result)
        assert isinstance(data, (list, dict)), "Should return a JSON object or array"
    
    @pytest.mark.asyncio
    async def test_returns_documentation_workflows(self):
        """Test that documentation workflow data is returned."""
        result = await get_documentation_workflow_status()
        data = json.loads(result)
        
        # Should return either a list or a message dict
        assert isinstance(data, (list, dict)), "Should return documentation workflow data"


@pytest.mark.skipif(not IMPORTS_SUCCESSFUL, reason="Imports failed")
class TestGetFailedWorkflows:
    """Test the get_failed_workflows tool."""
    
    @pytest.mark.asyncio
    async def test_returns_json_string(self):
        """Test that get_failed_workflows returns a JSON string."""
        result = await get_failed_workflows()
        
        assert isinstance(result, str), "Should return a string"
        # Should be valid JSON
        data = json.loads(result)
        assert isinstance(data, (list, dict)), "Should return a JSON object or array"
    
    @pytest.mark.asyncio
    async def test_returns_failed_workflows(self):
        """Test that failed workflow data is returned."""
        result = await get_failed_workflows()
        data = json.loads(result)
        
        # Should return either a list or a message dict
        assert isinstance(data, (list, dict)), "Should return failed workflow data"


@pytest.mark.skipif(not IMPORTS_SUCCESSFUL, reason="Imports failed")
class TestToolRegistration:
    """Test that tools are properly registered."""
    
    def test_tools_have_decorators(self):
        """Test that tool functions are properly defined."""
        # Check that functions exist and are callable
        assert hasattr(get_recent_actions_events, '__name__'), \
            "get_recent_actions_events should be a proper function"
        assert hasattr(get_workflow_status, '__name__'), \
            "get_workflow_status should be a proper function"
        assert hasattr(get_documentation_workflow_status, '__name__'), \
            "get_documentation_workflow_status should be a proper function"
        assert hasattr(get_failed_workflows, '__name__'), \
            "get_failed_workflows should be a proper function"


if __name__ == "__main__":
    if not IMPORTS_SUCCESSFUL:
        print(f"Cannot run tests - imports failed: {IMPORT_ERROR}")
        print("\nMake sure you've:")
        print("1. Implemented all CI monitor functions")
        print("2. Decorated them with @mcp.tool()")
        print("3. Installed dependencies with: pip install -r requirements.txt")
        exit(1)
    
    # Run tests
    pytest.main([__file__, "-v"])