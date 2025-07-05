# MCP-AutoPRX Production Server

A production-ready MCP (Model Context Protocol) server for automated PR analysis, CI/CD monitoring, and multi-platform notifications. Deployed on Railway for 24/7 availability.

## Features

- GitHub webhook event handling
- Automated PR analysis and file change detection
- Smart PR template suggestions based on change type
- CI/CD workflow monitoring
- Slack and Gmail notifications
- MCP protocol compliance
- Production-ready FastAPI server
- Railway cloud deployment

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export SLACK_WEBHOOK_URL=your_slack_webhook_url
export GMAIL_USER=your_email@gmail.com
export GMAIL_APP_PASSWORD=your_gmail_app_password
export DEFAULT_EMAIL_RECIPIENT=recipient@example.com
```

3. Run the unified server:
```bash
python unified_server.py
```

### Railway Deployment

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Deploy to Railway:
```bash
railway login
railway init
railway up
```

3. Set environment variables in Railway dashboard:
```
SLACK_WEBHOOK_URL=your_slack_webhook_url
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
DEFAULT_EMAIL_RECIPIENT=recipient@example.com
GITHUB_WEBHOOK_SECRET=your_webhook_secret
```

4. Configure GitHub webhooks:
   - URL: `https://your-app-name.up.railway.app/webhook/github`
   - Content type: `application/json`
   - Secret: (same as GITHUB_WEBHOOK_SECRET)

## Server Endpoints

- `GET /` - Server information
- `GET /health` - Health check
- `GET /tools` - List available tools
- `POST /webhook/github` - GitHub webhook handler
- `POST /mcp` - MCP protocol endpoint
- `POST /call/{tool_name}` - Direct tool calling

## Available Tools

### PR Analysis Tools
- `analyze_file_changes` - Analyze git file changes and generate summaries
- `get_pr_templates` - Get available PR templates with metadata

### CI/CD Monitoring Tools
- `get_recent_actions_events` - Get recent GitHub Actions events
- `get_workflow_status` - Get current status of GitHub Actions workflows
- `get_documentation_workflow_status` - Get status of documentation-related workflows
- `get_failed_workflows` - Get only failed workflows for troubleshooting

### Notification Tools
- `send_slack_notification` - Send Slack notification
- `send_gmail_notification` - Send Gmail notification

## Environment Variables

### Required
- `SLACK_WEBHOOK_URL` - Slack webhook URL
- `GMAIL_USER` - Gmail address
- `GMAIL_APP_PASSWORD` - Gmail app password
- `DEFAULT_EMAIL_RECIPIENT` - Default email recipient

### Optional
- `GITHUB_WEBHOOK_SECRET` - GitHub webhook secret
- `PORT` - Server port (Railway sets automatically)

## Project Structure

```
MCP-AutoPRX/
├── unified_server.py      # Main production server
├── railway.json          # Railway deployment config
├── requirements.txt      # Python dependencies
├── github_events.json   # GitHub events storage
├── mcp-server/          # MCP server components
│   ├── tools/           # MCP tools
│   ├── prompts/         # AI prompts
│   └── mcp_instance.py  # MCP instance
├── templates/           # PR templates
├── test/               # Test suite
└── .github/workflows/   # CI/CD workflows
    ├── build_documentation.yml      # Main CI/CD pipeline
    ├── upload_pr_documentation.yml  # Deployment preparation
    └── build_pr_documentation.yml   # PR testing
```

## Testing

Run the test suite:
```bash
python -m pytest test/ -v
```

Test individual components:
```bash
python -m pytest test/test_server.py -v
python -m pytest test/test_pr_analysis.py -v
python -m pytest test/test_ci_monitor.py -v
python -m pytest test/test_slack_notifier.py -v
```

Run async tests:
```bash
python -m pytest test/ -m asyncio
```

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment. The CI/CD pipeline ensures code quality, automated testing, and seamless deployment to Railway.

### GitHub Actions Workflows

#### 1. Build Documentation (`build_documentation.yml`)
**Purpose**: Main CI/CD pipeline for comprehensive testing and validation.

**Triggers**:
- Push to main branch
- Pull requests to main branch

**What it does**:
- Sets up Python 3.10 environment
- Installs all dependencies including test packages
- Runs comprehensive test suite with verbose output
- Validates server health and readiness
- Ensures code quality before deployment

**Key Features**:
- Early failure detection (`-x` flag stops on first failure)
- Comprehensive dependency installation
- Server health validation
- Documentation build verification

#### 2. Deploy Preparation (`upload_pr_documentation.yml`)
**Purpose**: Prepares and validates the project for Railway deployment.

**Triggers**:
- Push to main branch only

**What it does**:
- Validates server configuration files
- Checks Railway configuration presence
- Prepares deployment environment
- Ensures all required files are present

**Key Features**:
- Server file validation (`unified_server.py`)
- Railway configuration verification (`railway.json`)
- Deployment readiness confirmation
- Environment validation

#### 3. PR Testing (`build_pr_documentation.yml`)
**Purpose**: Comprehensive testing for pull requests.

**Triggers**:
- Pull requests to main branch only

**What it does**:
- Runs PR-specific test suite
- Validates code quality
- Ensures PR meets quality standards
- Provides feedback before merge

**Key Features**:
- PR-specific testing environment
- Code quality validation
- Early feedback for contributors
- Prevents breaking changes

### Workflow Configuration

All workflows use:
- **Python 3.10**: Required for MCP compatibility
- **Ubuntu Latest**: Consistent CI environment
- **Comprehensive Dependencies**: All test and runtime dependencies
- **Verbose Output**: Detailed error reporting for debugging

### Workflow Commands

Monitor workflow status:
```bash
# Check all workflow runs
gh run list

# View specific workflow logs
gh run view <run-id>

# Rerun failed workflow
gh run rerun <run-id>

# Check specific workflow
gh run list --workflow=build_documentation.yml
```

### CI/CD Benefits

- **Automated Quality Assurance**: Every push and PR is automatically tested
- **Early Issue Detection**: Problems are caught before they reach production
- **Consistent Environment**: All tests run in the same environment
- **Deployment Safety**: Server configuration is validated before deployment
- **Developer Experience**: Immediate feedback on code changes

## Railway Configuration

The `railway.json` file configures:
- Build process using Nixpacks
- Start command: `python unified_server.py`
- Health check endpoint: `/health`
- Automatic restart on failure
- Maximum 10 retry attempts

## Security Considerations

- Webhook secret validation
- Environment variable protection
- CORS configuration for production
- Rate limiting (consider implementing)
- HTTPS provided by Railway

## Documentation

This project includes comprehensive documentation:

- **README.md** - This file, project overview and quick start
- **PROJECT_KNOWLEDGE_BASE.md** - Comprehensive project knowledge and architecture
- **QUICK_REFERENCE.md** - Quick commands and API reference
- **TROUBLESHOOTING_GUIDE.md** - Common issues and solutions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

**Note**: All pull requests are automatically tested by the CI/CD pipeline before merging.

## License

MIT License - see LICENSE file for details.