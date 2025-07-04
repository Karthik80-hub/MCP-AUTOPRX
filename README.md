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
- `get_pr_templates` - Get available PR templates for different change types
- `suggest_template` - Suggest appropriate PR template based on changes

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
└── test/               # Test suite
```

## Testing

Run the test suite:
```bash
pytest
```

Test individual components:
```bash
python -m pytest test/test_server.py
python -m pytest test/test_pr_analysis.py
python -m pytest test/test_slack_notifier.py
```

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.