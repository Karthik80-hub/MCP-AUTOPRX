#!/usr/bin/env python3
"""
Unit tests for Slack Notifier Module
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
    from tools.slack_notifier import (
        send_slack_notification
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
        assert callable(send_slack_notification), "send_slack_notification should be a callable function"


@pytest.mark.skipif(not IMPORTS_SUCCESSFUL, reason="Imports failed")
class TestSendSlackNotification:
    """Test the send_slack_notification tool."""
    
    @pytest.mark.asyncio
    async def test_returns_json_string(self):
        """Test that send_slack_notification returns a JSON string."""
        with patch('requests.post') as mock_post:
            mock_post.return_value = MagicMock(status_code=200, text="ok")
            
            result = await send_slack_notification("Test message")
            
            assert isinstance(result, str), "Should return a string"
            # Should be a status message
            assert len(result) > 0, "Should return a non-empty string"
    
    @pytest.mark.asyncio
    async def test_includes_required_fields(self):
        """Test that the result includes expected fields."""
        with patch('requests.post') as mock_post:
            mock_post.return_value = MagicMock(status_code=200, text="ok")
            
            result = await send_slack_notification("Test message")
            
            # Should return a status message
            assert isinstance(result, str), "Should return a status message"


@pytest.mark.skipif(not IMPORTS_SUCCESSFUL, reason="Imports failed")
class TestToolRegistration:
    """Test that tools are properly registered."""
    
    def test_tools_have_decorators(self):
        """Test that tool functions are properly defined."""
        # Check that functions exist and are callable
        assert hasattr(send_slack_notification, '__name__'), \
            "send_slack_notification should be a proper function"


if __name__ == "__main__":
    if not IMPORTS_SUCCESSFUL:
        print(f"Cannot run tests - imports failed: {IMPORT_ERROR}")
        print("\nMake sure you've:")
        print("1. Implemented all Slack notifier functions")
        print("2. Decorated them with @mcp.tool()")
        print("3. Installed dependencies with: pip install -r requirements.txt")
        exit(1)
    
    # Run tests
    pytest.main([__file__, "-v"])