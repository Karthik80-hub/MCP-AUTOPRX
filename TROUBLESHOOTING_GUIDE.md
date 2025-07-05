# MCP-AutoPRX Troubleshooting Guide

## Overview
This document chronicles the issues encountered during the development and deployment of MCP-AutoPRX, along with their solutions. This serves as a reference for future development and helps others avoid similar pitfalls.

## Table of Contents
1. [GitHub Actions Workflow Issues](#github-actions-workflow-issues)
2. [Test Import and Module Issues](#test-import-and-module-issues)
3. [Dependency and Environment Issues](#dependency-and-environment-issues)
4. [Server Architecture Issues](#server-architecture-issues)
5. [CI/CD Pipeline Issues](#cicd-pipeline-issues)
6. [Deployment Issues](#deployment-issues)
7. [Lessons Learned](#lessons-learned)

---

## GitHub Actions Workflow Issues

### Issue 1: Non-existent Repository References
**Problem**: GitHub Actions workflows were referencing `huggingface/mcp-autoprx` instead of the actual repository.

**Error Message**:
```
Error: Process completed with exit code 1
Repository not found
```

**Root Cause**: Workflows were copied from a template and not updated for the specific project.

**Solution**:
1. Updated all workflow files to reference the correct repository
2. Changed Python version to 3.10 for MCP compatibility
3. Updated workflow names and descriptions

**Files Modified**:
- `.github/workflows/build_documentation.yml`
- `.github/workflows/test.yml`

### Issue 2: Python Version Compatibility
**Problem**: MCP package requires Python 3.10+, but workflows were using Python 3.8.

**Error Message**:
```
ImportError: cannot import name 'mcp' from 'mcp'
```

**Solution**:
```yaml
# Updated in workflow files
- uses: actions/setup-python@v4
  with:
    python-version: '3.10'
```

---

## Test Import and Module Issues

### Issue 3: Module Import Failures
**Problem**: Tests were trying to import from `server` module that no longer existed after unification.

**Error Message**:
```
ImportError: No module named 'server'
```

**Root Cause**: After creating the unified server architecture, old test files still referenced the deprecated `server` module.

**Solution**:
1. Updated all test files to import from correct modules:
   ```python
   # Old (incorrect)
   from server import analyze_file_changes
   
   # New (correct)
   from tools.pr_analysis import analyze_file_changes
   ```

2. Added proper path resolution:
   ```python
   import sys
   import os
   sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mcp-server')))
   ```

**Files Modified**:
- `test/test_ci_monitor.py`
- `test/test_pr_analysis.py`
- `test/test_slack_notifier.py`
- `test/test_server.py`

### Issue 4: Non-existent Function Imports
**Problem**: Tests were trying to import functions that didn't exist in the actual implementation.

**Error Message**:
```
ImportError: cannot import name 'suggest_template' from 'tools.pr_analysis'
ImportError: cannot import name 'send_pr_notification' from 'tools.slack_notifier'
```

**Root Cause**: Test files were written for a different implementation or outdated version.

**Solution**:
1. Updated imports to match actual available functions
2. Removed tests for non-existent functions
3. Updated test expectations to match actual return values

**Changes Made**:
- Removed `suggest_template` from PR analysis tests
- Removed `send_pr_notification` and `send_ci_notification` from Slack tests
- Updated template structure expectations

### Issue 5: Async Test Handling
**Problem**: Async tests were being skipped due to missing pytest-asyncio plugin.

**Error Message**:
```
PytestUnhandledCoroutineWarning: async def functions are not natively supported
```

**Solution**:
1. Added pytest-asyncio to requirements.txt:
   ```
   pytest-asyncio>=0.21.0
   ```

2. Updated test decorators to use proper async markers:
   ```python
   @pytest.mark.asyncio
   async def test_function():
       # test code
   ```

---

## Dependency and Environment Issues

### Issue 6: Missing Dependencies in CI
**Problem**: CI environment was missing required dependencies for testing.

**Error Message**:
```
ModuleNotFoundError: No module named 'pytest_asyncio'
```

**Solution**:
1. Updated requirements.txt to include all test dependencies
2. Ensured CI installs dependencies before running tests
3. Added explicit dependency installation in workflows

### Issue 7: Environment Variable Loading
**Problem**: Tests were failing because .env file wasn't available in CI.

**Error Message**:
```
FileNotFoundError: .env file not found
```

**Solution**:
1. Made environment variable loading optional in tests
2. Added fallback values for missing environment variables
3. Updated test configuration to handle missing .env files

---

## Server Architecture Issues

### Issue 8: FastAPI Import Errors
**Problem**: Server was failing to start due to missing FastAPI dependency.

**Error Message**:
```
ImportError: No module named 'fastapi'
```

**Solution**:
1. Added proper error handling for missing FastAPI
2. Added FastAPI to requirements.txt
3. Implemented graceful degradation when FastAPI is not available

### Issue 9: MCP Instance Configuration
**Problem**: MCP server instance wasn't properly configured for the unified architecture.

**Error Message**:
```
AttributeError: 'NoneType' object has no attribute 'tool'
```

**Solution**:
1. Updated MCP instance configuration
2. Ensured proper tool registration
3. Added error handling for MCP initialization failures

---

## CI/CD Pipeline Issues

### Issue 10: Test Execution Failures
**Problem**: Tests were failing due to incorrect expectations and missing setup.

**Error Message**:
```
AssertionError: assert 'name' in {'filename': 'bug.md', 'type': 'Bug Fix', 'content': '...'}
```

**Root Cause**: Test expectations didn't match actual implementation return values.

**Solution**:
1. Updated test expectations to match actual data structures
2. Fixed template structure validation
3. Added proper test data setup

**Example Fix**:
```python
# Old expectation
assert "name" in template

# New expectation
assert "filename" in template
assert "type" in template
assert "content" in template
```

### Issue 11: Workflow Configuration
**Problem**: GitHub Actions workflows weren't properly configured for the project structure.

**Error Message**:
```
Error: Process completed with exit code 1
```

**Solution**:
1. Updated workflow triggers and conditions
2. Fixed Python version requirements
3. Added proper error handling and reporting
4. Configured proper test execution order

---

## Deployment Issues

### Issue 12: Railway Deployment Configuration
**Problem**: Railway deployment wasn't properly configured for the unified server.

**Error Message**:
```
ModuleNotFoundError: No module named 'unified_server'
```

**Solution**:
1. Updated Railway configuration to use correct entry point
2. Fixed module import paths
3. Added proper environment variable configuration
4. Updated deployment scripts

---

## Lessons Learned

### 1. Module Path Management
**Lesson**: Always use absolute paths and proper sys.path manipulation when dealing with modular Python projects.

**Best Practice**:
```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mcp-server')))
```

### 2. Test-Driven Development
**Lesson**: Write tests that match the actual implementation, not idealized versions.

**Best Practice**:
- Test actual function signatures
- Use realistic test data
- Validate actual return structures

### 3. Dependency Management
**Lesson**: Always include test dependencies in requirements.txt for CI/CD environments.

**Best Practice**:
```
# Include in requirements.txt
pytest-asyncio>=0.21.0
pytest>=7.0.0
```

### 4. Error Handling
**Lesson**: Implement graceful degradation for missing dependencies and configuration.

**Best Practice**:
```python
try:
    import fastapi
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("Warning: FastAPI not available")
```

### 5. CI/CD Configuration
**Lesson**: Always test CI/CD workflows locally and ensure they match the actual project structure.

**Best Practice**:
- Use project-specific repository references
- Test workflows on feature branches
- Include proper error reporting

### 6. Documentation
**Lesson**: Keep documentation updated with actual implementation changes.

**Best Practice**:
- Update documentation with each major change
- Include troubleshooting guides
- Document breaking changes

---

## Prevention Strategies

### 1. Automated Testing
- Run tests before every commit
- Use pre-commit hooks
- Implement continuous testing

### 2. Dependency Management
- Use dependency lock files
- Regular dependency updates
- Test with minimal dependency sets

### 3. Environment Management
- Use environment-specific configurations
- Implement proper fallbacks
- Document all required environment variables

### 4. Code Review
- Review import statements
- Validate test expectations
- Check for hardcoded paths

### 5. Documentation
- Keep README files updated
- Document breaking changes
- Maintain troubleshooting guides

---

## Quick Fixes Reference

### Common Commands
```bash
# Fix import issues
python -c "import sys; print(sys.path)"

# Install missing dependencies
pip install pytest-asyncio

# Run tests with verbose output
python -m pytest test/ -v --tb=short

# Check module availability
python -c "import mcp; print('MCP available')"

# Validate environment
python -c "import os; print(os.getenv('SLACK_WEBHOOK_URL'))"
```

### Emergency Fixes
1. **Import Errors**: Check sys.path and module structure
2. **Test Failures**: Update test expectations to match implementation
3. **CI Failures**: Verify Python version and dependencies
4. **Deployment Issues**: Check Railway configuration and environment variables

---

This troubleshooting guide should be updated with each new issue encountered to maintain a comprehensive reference for future development. 