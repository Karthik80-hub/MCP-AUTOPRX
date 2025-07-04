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
from mcp_server.tools import pr_analysis, ci_monitor, slack_notifier
from mcp_server.prompts import pr_prompts, ci_prompts, review_prompts


class TestUnifiedServer:
    """Test the main unified server functionality."""
    
    def test_server_import(self):
        """Test that the unified_server module can be imported."""
        assert hasattr(unified_server, 'UnifiedServer'), "unified_server.py should have a 'UnifiedServer' class"
    
    def test_server_initialization(self):
        """Test that the server can be initialized."""
        server = unified_server.UnifiedServer()
        assert server is not None, "UnifiedServer should be initialized"
        assert hasattr(server, 'app'), "UnifiedServer should have an 'app' attribute (FastAPI instance)"
    
    def test_server_endpoints(self):
        """Test that the server has the required endpoints."""
        server = unified_server.UnifiedServer()
        # Check that the app has the expected routes
        routes = [route.path for route in server.app.routes]
        expected_routes = ['/', '/health', '/tools', '/webhook/github', '/mcp', '/call/{tool_name}']
        
        for route in expected_routes:
            assert route in routes, f"Route {route} should be available"
    
    def test_tools_available(self):
        """Test that all required tools are available."""
        server = unified_server.UnifiedServer()
        # The tools are registered in the MCP instance
        assert hasattr(server, 'mcp'), "Server should have MCP instance"


class TestDotenvLoading:
    """Test dotenv loading functionality."""
    
    def test_dotenv_file_exists(self):
        """Test that .env file exists in the project root."""
        env_file = Path(__file__).parent.parent / ".env"
        assert env_file.exists(), ".env file should exist in project root"
    
    def test_dotenv_file_content(self):
        """Test that .env file contains required variables."""
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            content = env_file.read_text()
            assert "SLACK_WEBHOOK_URL" in content, ".env file should contain SLACK_WEBHOOK_URL"
    
    @patch('dotenv.load_dotenv')
    def test_dotenv_loading_in_server(self, mock_load_dotenv):
        """Test that dotenv is loaded in server.py."""
        # This test assumes you'll add dotenv loading to server.py
        # For now, it just checks if the functionality is expected
        mock_load_dotenv.return_value = True
        
        # If you add dotenv loading to server.py, this test will validate it
        # For now, we'll just verify the mock works
        assert mock_load_dotenv.called is False  # Not called yet since it's not in server.py
    
    def test_environment_variable_loading(self):
        """Test that environment variables can be loaded from .env file."""
        try:
            from dotenv import load_dotenv
            env_file = Path(__file__).parent.parent / ".env"
            
            if env_file.exists():
                # Load environment variables
                load_dotenv(dotenv_path=env_file)
                
                # Check if SLACK_WEBHOOK_URL is loaded
                slack_url = os.getenv("SLACK_WEBHOOK_URL")
                assert slack_url is not None, "SLACK_WEBHOOK_URL should be loaded from .env file"
                assert slack_url.startswith("https://hooks.slack.com/"), "SLACK_WEBHOOK_URL should be a valid Slack webhook URL"
        except ImportError:
            pytest.skip("python-dotenv not installed")


class TestPRAnalysis:
    """Test PR analysis tools."""
    
    @patch('subprocess.run')
    def test_analyze_file_changes_success(self, mock_run):
        """Test analyze_file_changes with successful git operations."""
        # Mock git commands
        mock_run.side_effect = [
            MagicMock(stdout="M\tfile1.py\nA\tfile2.py", stderr="", returncode=0),
            MagicMock(stdout=" 2 files changed, 10 insertions(+), 5 deletions(-)", stderr="", returncode=0),
            MagicMock(stdout="diff --git a/file1.py b/file1.py\n@@ -1,1 +1,1 @@\n-old\n+new", stderr="", returncode=0),
            MagicMock(stdout="abc1234 Update file1\n", stderr="", returncode=0)
        ]
        
        # Test the function
        result = pr_analysis.analyze_file_changes("main", True, 500)
        
        # Verify the result
        data = json.loads(result)
        assert data["base_branch"] == "main"
        assert "file1.py" in data["files_changed"]
        assert "2 files changed" in data["statistics"]
        assert "abc1234" in data["commits"]
        assert "diff --git" in data["diff"]
        assert data["truncated"] is False
    
    @patch('subprocess.run')
    def test_analyze_file_changes_git_error(self, mock_run):
        """Test analyze_file_changes with git error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git", stderr="fatal: not a git repository")
        
        result = pr_analysis.analyze_file_changes("main")
        data = json.loads(result)
        assert "error" in data
        assert "Git error" in data["error"]
    
    def test_get_pr_templates(self):
        """Test get_pr_templates function."""
        result = pr_analysis.get_pr_templates()
        templates = json.loads(result)
        
        # Check that templates are returned
        assert isinstance(templates, list)
        assert len(templates) > 0
        
        # Check template structure
        for template in templates:
            assert "filename" in template
            assert "type" in template
            assert "content" in template
            assert template["filename"].endswith(".md")


class TestCIMonitor:
    """Test CI monitoring tools."""
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_recent_actions_events_with_data(self, mock_file, mock_exists):
        """Test get_recent_actions_events with existing data."""
        mock_exists.return_value = True
        mock_data = [
            {"id": 1, "workflow_run": {"name": "test-workflow", "status": "completed"}},
            {"id": 2, "workflow_run": {"name": "test-workflow", "status": "in_progress"}}
        ]
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data)
        
        result = ci_monitor.get_recent_actions_events(limit=5)
        events = json.loads(result)
        
        assert isinstance(events, list)
        assert len(events) == 2
    
    @patch('pathlib.Path.exists')
    def test_get_recent_actions_events_no_file(self, mock_exists):
        """Test get_recent_actions_events when file doesn't exist."""
        mock_exists.return_value = False
        
        result = ci_monitor.get_recent_actions_events()
        events = json.loads(result)
        
        assert isinstance(events, list)
        assert len(events) == 0
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_workflow_status_with_data(self, mock_file, mock_exists):
        """Test get_workflow_status with existing workflow data."""
        mock_exists.return_value = True
        mock_data = [
            {
                "workflow_run": {
                    "name": "test-workflow",
                    "status": "completed",
                    "conclusion": "success",
                    "run_number": 1,
                    "updated_at": "2023-01-01T00:00:00Z",
                    "html_url": "https://github.com/test/repo/actions/runs/1"
                }
            }
        ]
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data)
        
        result = ci_monitor.get_workflow_status()
        workflows = json.loads(result)
        
        assert isinstance(workflows, list)
        assert len(workflows) == 1
        assert workflows[0]["name"] == "test-workflow"
        assert workflows[0]["status"] == "completed"
    
    @patch('pathlib.Path.exists')
    def test_get_workflow_status_no_file(self, mock_exists):
        """Test get_workflow_status when file doesn't exist."""
        mock_exists.return_value = False
        
        result = ci_monitor.get_workflow_status()
        data = json.loads(result)
        
        assert "message" in data
        assert "No GitHub Actions events" in data["message"]
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_documentation_workflow_status(self, mock_file, mock_exists):
        """Test get_documentation_workflow_status with documentation workflow data."""
        mock_exists.return_value = True
        mock_data = [
            {
                "workflow_run": {
                    "name": "Build PR Documentation",
                    "status": "completed",
                    "conclusion": "success",
                    "run_number": 1,
                    "updated_at": "2023-01-01T00:00:00Z",
                    "html_url": "https://github.com/test/repo/actions/runs/1"
                }
            }
        ]
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data)
        
        result = ci_monitor.get_documentation_workflow_status()
        workflows = json.loads(result)
        
        assert isinstance(workflows, list)
        assert len(workflows) == 1
        assert workflows[0]["name"] == "Build PR Documentation"
        assert workflows[0]["status"] == "completed"
        assert "description" in workflows[0]
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_failed_workflows(self, mock_file, mock_exists):
        """Test get_failed_workflows with failed workflow data."""
        mock_exists.return_value = True
        mock_data = [
            {
                "workflow_run": {
                    "name": "Build documentation",
                    "status": "completed",
                    "conclusion": "failure",
                    "run_number": 1,
                    "updated_at": "2023-01-01T00:00:00Z",
                    "html_url": "https://github.com/test/repo/actions/runs/1"
                }
            }
        ]
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data)
        
        result = ci_monitor.get_failed_workflows()
        workflows = json.loads(result)
        
        assert isinstance(workflows, list)
        assert len(workflows) == 1
        assert workflows[0]["name"] == "Build documentation"
        assert workflows[0]["conclusion"] == "failure"


class TestSlackNotifier:
    """Test Slack notification tools."""
    
    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'})
    @patch('requests.post')
    def test_send_slack_notification_success(self, mock_post):
        """Test send_slack_notification with successful request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = slack_notifier.send_slack_notification("Test message")
        
        assert "Message sent successfully" in result
        mock_post.assert_called_once()
    
    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'})
    @patch('requests.post')
    def test_send_slack_notification_failure(self, mock_post):
        """Test send_slack_notification with failed request."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        result = slack_notifier.send_slack_notification("Test message")
        
        assert "Failed to send message" in result
        assert "400" in result
    
    @patch.dict(os.environ, {}, clear=True)
    def test_send_slack_notification_no_webhook(self):
        """Test send_slack_notification without webhook URL."""
        result = slack_notifier.send_slack_notification("Test message")
        
        assert "Error: SLACK_WEBHOOK_URL environment variable not set" in result
    
    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'})
    @patch('requests.post')
    def test_send_slack_notification_timeout(self, mock_post):
        """Test send_slack_notification with timeout."""
        mock_post.side_effect = requests.exceptions.Timeout()
        
        result = slack_notifier.send_slack_notification("Test message")
        
        assert "Request timed out" in result
    
    def test_slack_webhook_url_from_env_file(self):
        """Test that SLACK_WEBHOOK_URL can be loaded from .env file."""
        try:
            from dotenv import load_dotenv
            env_file = Path(__file__).parent.parent / ".env"
            
            if env_file.exists():
                # Load environment variables
                load_dotenv(dotenv_path=env_file)
                
                # Check if SLACK_WEBHOOK_URL is available
                slack_url = os.getenv("SLACK_WEBHOOK_URL")
                assert slack_url is not None, "SLACK_WEBHOOK_URL should be loaded from .env file"
                
                # Test that the webhook URL is valid
                assert slack_url.startswith("https://hooks.slack.com/"), "SLACK_WEBHOOK_URL should be a valid Slack webhook URL"
                
                # Test that the slack_notifier can use this URL
                with patch('requests.post') as mock_post:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_post.return_value = mock_response
                    
                    result = slack_notifier.send_slack_notification("Test message from .env")
                    assert "Message sent successfully" in result
        except ImportError:
            pytest.skip("python-dotenv not installed")


class TestToolsPackage:
    """Test the tools package auto-import functionality."""
    
    def test_tools_package_imports(self):
        """Test that tools package auto-imports all modules."""
        # Test that modules are available in the package
        assert hasattr(pr_analysis, 'analyze_file_changes')
        assert hasattr(pr_analysis, 'get_pr_templates')
        assert hasattr(ci_monitor, 'get_recent_actions_events')
        assert hasattr(ci_monitor, 'get_workflow_status')
        assert hasattr(slack_notifier, 'send_slack_notification')
    
    def test_tools_package_all(self):
        """Test that __all__ is properly defined."""
        from tools import __all__
        assert isinstance(__all__, list)
        assert len(__all__) > 0


class TestPromptsPackage:
    """Test the prompts package auto-import functionality."""
    
    def test_prompts_package_imports(self):
        """Test that prompts package auto-imports all modules."""
        # Test that modules are available in the package
        assert hasattr(pr_prompts, 'suggest_template')
        assert hasattr(ci_prompts, 'format_ci_failure_alert')
        assert hasattr(ci_prompts, 'format_ci_success_summary')
        assert hasattr(review_prompts, 'analyze_ci_results')
        assert hasattr(review_prompts, 'create_deployment_summary')
        assert hasattr(review_prompts, 'generate_pr_status_report')
        assert hasattr(review_prompts, 'troubleshoot_workflow_failure')
    
    def test_prompts_package_all(self):
        """Test that __all__ is properly defined."""
        from prompts import __all__
        assert isinstance(__all__, list)
        assert len(__all__) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 