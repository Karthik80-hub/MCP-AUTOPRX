# MCP-AutoPRX: Automated GitHub PR & CI Monitor

## What is MCP-AutoPRX?

**MCP-AutoPRX** is a production-ready unified server that combines GitHub automation, CI/CD monitoring, and LLM integration using the Model Context Protocol (MCP). It serves as a bridge between GitHub events and AI-powered analysis, enabling intelligent automation of development workflows.

## What Does This Server Do?

This server provides three main services in a single unified application:

1. **GitHub Webhook Handler** - Receives and processes GitHub events (pushes, PRs, CI/CD runs)
2. **MCP (Model Context Protocol) Server** - Exposes tools for LLMs to analyze code and manage workflows
3. **Multi-Platform Notification System** - Sends alerts to Slack and Gmail for important events

## Real-World LLM Integration

### How LLMs Use This Server

LLMs (like Claude, GPT-4, etc.) can interact with this server through:

1. **MCP Protocol** - Direct integration using the Model Context Protocol
2. **REST API** - HTTP endpoints for tool calling
3. **Webhook Processing** - Automatic event handling and notifications

### Use Cases

- **Automated PR Analysis** - LLMs analyze code changes and suggest improvements
- **CI/CD Monitoring** - Real-time monitoring of build and deployment status
- **Intelligent Notifications** - AI-powered alert filtering and prioritization
- **Workflow Automation** - LLMs trigger actions based on GitHub events

**MCP-AutoPRX** is an intelligent GitHub automation server built using Claude and the Model Context Protocol (MCP). It helps teams:

* Automatically generate meaningful PR descriptions
* Detect and notify about CI/CD failures via Slack and Gmail
* Run an end-to-end automation pipeline with Claude as the brain

**Live Server**: https://mcp-autoprx-production.up.railway.app

**Health Check**: https://mcp-autoprx-production.up.railway.app/health

**API Documentation**: https://mcp-autoprx-production.up.railway.app/docs

---

## Features

* Analyze git diffs and generate detailed change summaries
* Capture GitHub Action events in real time via webhooks
* Provide intelligent PR template suggestions based on change types
* Notify teams of CI failures on Slack or via Gmail
* Railway cloud deployment with 24/7 availability
* Integrates with Claude Code for prompt-driven automation
* Production-ready security with API key protection
* Comprehensive monitoring and health checks

## Solve PR Chaos

Transform cryptic pull requests like "stuff" and "more changes" into clear, actionable descriptions. Your server analyzes code changes and helps LLMs generate meaningful PR descriptions that reviewers can actually understand.

---

## Technical Stack

### Backend
- **Framework**: FastAPI
- **MCP Library**: FastMCP
- **Language**: Python 3.10+
- **Server**: Uvicorn ASGI
- **Deployment**: Railway Cloud Platform

### AI/ML Integration
- **Model Context Protocol (MCP)**: Core LLM integration
- **Claude Integration**: Direct Claude Code support
- **Git Analysis**: Advanced git diff processing
- **Template Intelligence**: AI-powered template suggestions

### Infrastructure
- **Cloud Platform**: Railway
- **CI/CD**: GitHub Actions
- **Database**: JSON file storage (github_events.json)
- **Security**: API key authentication, GitHub webhook verification
- **SSL/TLS**: Automatic HTTPS via Railway

### External Integrations
- **GitHub Webhooks**: Real-time event processing
- **Slack API**: Notification delivery
- **Gmail SMTP**: Email notifications
- **Git Commands**: Local git analysis

---

## Project Structure

```
MCP-AutoPRX/
├── unified_server.py      # Main FastAPI server with all endpoints
├── railway.json          # Railway deployment configuration
├── requirements.txt      # Python dependencies
├── github_events.json   # GitHub events storage
├── mcp-server/          # MCP server components
│   ├── tools/           # MCP tools implementation
│   │   ├── pr_analysis.py      # Git analysis and PR tools
│   │   ├── ci_monitor.py       # CI/CD monitoring tools
│   │   ├── slack_notifier.py   # Slack notification tools
│   │   └── gmail_notifier.py   # Gmail notification tools
│   ├── prompts/         # AI prompts and templates
│   │   ├── pr_prompts.py       # PR-related prompts
│   │   ├── ci_prompts.py       # CI/CD prompts
│   │   └── review_prompts.py   # Code review prompts
│   └── mcp_instance.py  # Shared MCP instance
├── templates/           # PR templates
│   ├── bug.md          # Bug fix template
│   ├── feature.md      # Feature template
│   ├── docs.md         # Documentation template
│   ├── refactor.md     # Refactor template
│   ├── test.md         # Test template
│   ├── performance.md  # Performance template
│   └── security.md     # Security template
├── test/               # Test suite
│   ├── test_server.py  # Server tests
│   ├── test_pr_analysis.py  # PR analysis tests
│   ├── test_ci_monitor.py   # CI monitoring tests
│   └── test_slack_notifier.py  # Notification tests
└── .github/workflows/   # CI/CD workflows
```

---

## Usage

### For LLM Developers
1. **Connect via MCP Protocol**
   ```bash
   claude-code --mcp-server python unified_server.py
   ```

2. **Use REST API**
   ```bash
   curl -H "x-api-key: your_api_key" \
        https://mcp-autoprx-production.up.railway.app/tools
   ```

3. **Call Tools Directly**
   ```bash
   curl -X POST https://mcp-autoprx-production.up.railway.app/call/analyze_file_changes \
     -H "x-api-key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{"arguments": {"base_branch": "main"}}'
   ```

### For DevOps Teams
1. **Configure GitHub Webhooks**
   - URL: `https://mcp-autoprx-production.up.railway.app/webhook/github`
   - Events: push, pull_request, workflow_run, check_suite, status, deployment_status

2. **Set Environment Variables**
   ```bash
   SLACK_WEBHOOK_URL=your_slack_webhook
   GMAIL_USER=your_email@gmail.com
   GMAIL_APP_PASSWORD=your_app_password
   DEFAULT_EMAIL_RECIPIENT=recipient@example.com
   MCP_API_KEY=your_secure_api_key
   GITHUB_WEBHOOK_SECRET=your_webhook_secret
   ```

3. **Monitor Health**
   ```bash
   curl https://mcp-autoprx-production.up.railway.app/health
   ```

### For Development Teams
1. **Analyze Code Changes**
   - Use `analyze_file_changes` to understand what changed
   - Get detailed git diffs and commit history
   - Understand file modifications and impact

2. **Get PR Templates**
   - Use `get_pr_templates` to see available templates
   - Use `suggest_template` for AI-powered recommendations
   - Generate meaningful PR descriptions

3. **Monitor CI/CD**
   - Track workflow status with `get_workflow_status`
   - Get recent events with `get_recent_actions_events`
   - Monitor failed workflows with `get_failed_workflows`

---

## Development

### Key Components

#### Core Server (`unified_server.py`)
- **FastAPI Application**: Main server with all endpoints
- **MCP Integration**: FastMCP server for LLM tools
- **Webhook Handler**: GitHub event processing
- **Notification System**: Slack and Gmail integration
- **Security Middleware**: API key protection

#### MCP Tools (`mcp-server/tools/`)
- **PR Analysis Tools**: Git analysis and template suggestions
- **CI/CD Monitoring**: Workflow status tracking
- **Notification Tools**: Slack and Gmail message sending
- **Event Processing**: GitHub webhook data handling

#### AI Prompts (`mcp-server/prompts/`)
- **PR Prompts**: Template suggestion logic
- **CI Prompts**: Workflow analysis prompts
- **Review Prompts**: Code review assistance

### Database Schema
- **GitHub Events**: Stored in `github_events.json`
- **Event Structure**: Timestamp, event type, repository, sender, full data
- **Storage Limit**: Last 100 events kept
- **Data Format**: JSON with full event details

### API Endpoints
- **Public**: `/`, `/health`, `/docs`, `/webhook/github`
- **Protected**: `/tools`, `/mcp`, `/call/{tool_name}`, `/test-email`
- **Authentication**: API key required for protected endpoints

---

## Security

### Authentication
- **API Key Protection**: Sensitive endpoints require `x-api-key` header
- **GitHub Webhook Verification**: HMAC-SHA256 signature validation
- **Environment Variables**: Secure storage in Railway

### Best Practices
- **Strong API Keys**: 32+ character random keys
- **Webhook Secrets**: Unique secrets for each repository
- **HTTPS Only**: Automatic SSL/TLS via Railway
- **Input Validation**: All webhook data validated
- **Error Handling**: Secure error responses

### Security Checklist
- [ ] API key set and used
- [ ] GitHub webhook secret configured
- [ ] Environment variables secured
- [ ] HTTPS enabled
- [ ] No credentials in code
- [ ] Input validation implemented
- [ ] Access logging enabled

---

## Testing

### Automated Testing
```bash
# Run all tests
python -m pytest test/ -v

# Test specific components
python -m pytest test/test_server.py -v
python -m pytest test/test_pr_analysis.py -v
python -m pytest test/test_ci_monitor.py -v
python -m pytest test/test_slack_notifier.py -v
```

### Manual Testing
```bash
# Test health endpoint
curl https://mcp-autoprx-production.up.railway.app/health

# Test Gmail functionality
curl https://mcp-autoprx-production.up.railway.app/test-email

# Test webhook with sample data
curl -X POST https://mcp-autoprx-production.up.railway.app/webhook/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: workflow_run" \
  -d '{"action": "completed", "workflow_run": {...}}'
```

---

## Deployment

### Railway Deployment
1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy to Railway**
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Configure Environment Variables**
   ```bash
   railway variables set SLACK_WEBHOOK_URL=your_url
   railway variables set GMAIL_USER=your_email
   railway variables set GMAIL_APP_PASSWORD=your_password
   railway variables set DEFAULT_EMAIL_RECIPIENT=recipient@example.com
   railway variables set MCP_API_KEY=your_api_key
   railway variables set GITHUB_WEBHOOK_SECRET=your_secret
   ```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SLACK_WEBHOOK_URL=your_url
export GMAIL_USER=your_email
export GMAIL_APP_PASSWORD=your_password
export DEFAULT_EMAIL_RECIPIENT=recipient@example.com

# Run server
python unified_server.py
```

---

## Contributing

We welcome contributions to MCP-AutoPRX! Here's how you can help:

### Development Setup
1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/MCP-AutoPRX.git
   cd MCP-AutoPRX
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Make your changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

6. **Test your changes**
   ```bash
   python -m pytest test/ -v
   ```

7. **Commit and push**
   ```bash
   git add .
   git commit -m 'Add some AmazingFeature'
   git push origin feature/AmazingFeature
   ```

8. **Open a Pull Request**

### Contribution Guidelines
- **Code Style**: Follow PEP 8 Python guidelines
- **Testing**: Add tests for new features
- **Documentation**: Update README.md and docstrings
- **Security**: Follow security best practices
- **Performance**: Consider impact on response times

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**Karthik Chunchu** - AI/ML Engineer & Full Stack Developer
- **GitHub**: [@Karthik80-hub](https://github.com/Karthik80-hub)
- **Live Demo**: [MCP-AutoPRX Server](https://mcp-autoprx-production.up.railway.app)

---

## Acknowledgments

- **FastAPI** framework and community
- **FastMCP** library for MCP implementation
- **Railway** for cloud deployment
- **GitHub** for webhook infrastructure
- **Claude** and **Anthropic** for LLM integration
- **OpenAI** for GPT integration support
- All contributors to the project

---

## Contact

For any queries, support, or feature requests:
- **GitHub Issues**: Open an issue in the repository
- **Live Server**: https://mcp-autoprx-production.up.railway.app
- **Health Check**: https://mcp-autoprx-production.up.railway.app/health
- **API Documentation**: https://mcp-autoprx-production.up.railway.app/docs

---

**Last Updated**: December 2024 - Production deployment with full CI/CD integration