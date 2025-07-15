# MCP-AutoPRX: Automated GitHub PR & CI Monitor

## What is MCP-AutoPRX?

**MCP-AutoPRX** is a production-ready unified server that combines GitHub automation, CI/CD monitoring, and LLM integration using the Model Context Protocol (MCP). It serves as a bridge between GitHub events and AI-powered analysis, enabling intelligent automation of development workflows.

## What Does This Server Do?

This server provides three main services in a single unified application:

1. **GitHub Webhook Handler** - Receives and processes GitHub events (pushes, PRs, CI/CD runs)
2. **MCP (Model Context Protocol) Server** - Exposes tools for LLMs to analyze code and manage workflows
3. **Multi-Platform Notification System** - Sends alerts to Slack and Gmail for important events

## Universal LLM Integration

### Compatible with Any LLM Platform

Your MCP-AutoPRX server can integrate with **virtually any LLM** that supports HTTP APIs or the Model Context Protocol (MCP). This makes it a universal tool provider for AI systems.

### Supported LLM Platforms

#### **Claude (Anthropic)**
- **Native MCP Support**: Direct integration via Model Context Protocol
- **Claude Code**: Built-in support for MCP servers
- **Command**: `claude-code --mcp-server python unified_server.py`

#### **OpenAI GPT Models**
- **Function Calling**: Use your tools as external functions
- **HTTP API Integration**: Direct REST API calls
- **Custom Functions**: Define your tools in GPT function schemas

#### **Google Gemini**
- **HTTP API Integration**: Call your endpoints directly
- **External Tools**: Use your server as external service provider
- **Function Calling**: Similar to GPT integration

#### **Local LLMs (Ollama, etc.)**
- **HTTP Endpoints**: Universal compatibility via REST APIs
- **Custom Integrations**: Direct API calls to your tools
- **External Data**: Access GitHub data through your server

#### **Custom AI Applications**
- **Any HTTP Client**: Universal web standard compatibility
- **JSON Communication**: Standard data format support
- **Authentication**: API key protection for security

### Integration Methods

#### **1. MCP Protocol (Recommended for Claude)**
```bash
# Direct MCP integration
claude-code --mcp-server python unified_server.py

# Or add your deployed server to Claude:
claude mcp add --transport sse autoprx-server https://mcp-autoprx-production.up.railway.app/mcp

# Claude can then use all your tools:
# - analyze_file_changes
# - get_pr_templates
# - send_slack_notification
# - send_gmail_notification
```

#### **2. HTTP REST API (Universal)**
```python
import requests

# Get available tools
response = requests.get(
    "https://mcp-autoprx-production.up.railway.app/tools",
    headers={"x-api-key": "your_api_key"}  # Replace with your actual API key
)

# Execute any tool
response = requests.post(
    "https://mcp-autoprx-production.up.railway.app/call/analyze_file_changes",
    headers={
        "Content-Type": "application/json",
        "x-api-key": "your_api_key"  # Replace with your actual API key
    },
    json={"arguments": {"base_branch": "main"}}
)
```

#### **3. Function Calling (GPT/Gemini)**
Define your tools as functions for LLM platforms:
```json
{
  "type": "function",
  "function": {
    "name": "analyze_file_changes",
    "description": "Analyze git file changes and generate summaries",
    "parameters": {
      "type": "object",
      "properties": {
        "base_branch": {"type": "string"},
        "include_diff": {"type": "boolean"},
        "max_diff_lines": {"type": "integer"}
      }
    }
  }
}
```

### Real-World Use Cases

#### **Automated PR Analysis**
- LLMs analyze code changes and suggest improvements
- Generate meaningful PR descriptions from cryptic commits
- Identify potential issues before code review

#### **CI/CD Monitoring**
- Real-time monitoring of build and deployment status
- AI-powered failure analysis and suggestions
- Intelligent alert filtering and prioritization

#### **Workflow Automation**
- LLMs trigger actions based on GitHub events
- Automated response to CI failures
- Smart notification routing

#### **Code Review Assistance**
- AI-powered code analysis and suggestions
- Template recommendations based on change types
- Automated documentation updates

### Why Your Server is Universal

1. **MCP Protocol** - Industry standard for LLM tool integration
2. **HTTP REST API** - Universal web standard compatibility
3. **JSON Communication** - Standard data format for all platforms
4. **Authentication** - API key protection for secure access
5. **Documentation** - Swagger UI for easy integration
6. **Cloud Deployment** - Always available via Railway

### Getting Started with LLM Integration

1. **Get Your API Key**: Set `MCP_API_KEY` environment variable in Railway
2. **Choose Integration Method**: MCP for Claude, HTTP for others
3. **Test Connection**: Use the `/tools` endpoint to verify
4. **Start Building**: Integrate tools into your LLM workflows

**Your server is essentially a universal LLM tool provider that works with any AI system!**

**MCP-AutoPRX** is an intelligent GitHub automation server built using Claude and the Model Context Protocol (MCP). It helps teams:

* Automatically generate meaningful PR descriptions
* Detect and notify about CI/CD failures via Slack and Gmail
* Run an end-to-end automation pipeline with Claude as the brain

**Live Server**: https://mcp-autoprx-production.up.railway.app

**Health Check**: https://mcp-autoprx-production.up.railway.app/health

**API Documentation**: https://mcp-autoprx-production.up.railway.app/docs

---

## Deploy Your Own Instance

**Why deploy your own?** This repository provides a live demo server, but we recommend deploying your own instance for:

- **Security**: Full control over your API keys and data
- **Performance**: No shared resources or rate limits
- **Customization**: Modify tools and workflows for your needs
- **Learning**: Understand the technology by deploying it yourself
- **Production Use**: Reliable, isolated environment for your team

### Quick Deployment Steps

1. **Fork this repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/MCP-AutoPRX.git
   cd MCP-AutoPRX
   ```

2. **Deploy to Railway**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and deploy
   railway login
   railway init
   railway up
   ```

3. **Configure Environment Variables**
   ```bash
   # Set your own secure API key
   railway variables set MCP_API_KEY=your_secure_random_key_here
   
   # Configure notifications (optional)
   railway variables set SLACK_WEBHOOK_URL=your_slack_webhook
   railway variables set GMAIL_USER=your_email@gmail.com
   railway variables set GMAIL_APP_PASSWORD=your_app_password
   railway variables set DEFAULT_EMAIL_RECIPIENT=recipient@example.com
   
   # GitHub webhook security (recommended)
   railway variables set GITHUB_WEBHOOK_SECRET=your_webhook_secret
   ```

4. **Get Your Server URL**
   ```bash
   # Find your deployment URL
   railway status
   # Your server will be available at: https://your-app-name.up.railway.app
   ```

5. **Register with Claude**
   ```bash
   # Use your own server URL
   claude mcp add --transport sse autoprx-server https://your-app-name.up.railway.app/mcp
   ```

### Benefits of Self-Deployment

| Aspect | Shared Server | Your Own Instance |
|--------|---------------|-------------------|
| **Security** | Shared API key | Your own API key |
| **Data Privacy** | Shared storage | Your own data |
| **Customization** | Limited | Full control |
| **Rate Limits** | Shared | Your own limits |
| **Reliability** | Depends on others | Your own uptime |
| **Cost** | Free | Railway free tier |

**Ready to deploy?** Follow the steps above and you'll have your own production-ready MCP server in minutes!

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
   curl -H "x-api-key: YOUR_API_KEY" \
        https://mcp-autoprx-production.up.railway.app/tools
   ```

3. **Call Tools Directly**
   ```bash
   curl -X POST https://mcp-autoprx-production.up.railway.app/call/analyze_file_changes \
     -H "x-api-key: YOUR_API_KEY" \
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
   MCP_API_KEY=your_secure_api_key  # Generate a secure random key
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

## Claude Integration & MCP Commands

### Register Your MCP Server with Claude

To add your deployed MCP server to Claude:

```bash
claude mcp add --transport sse autoprx-server https://mcp-autoprx-production.up.railway.app/mcp
```

This will register your server as an MCP tool provider in Claude Code.

### Test Your MCP Server in Claude

Once registered, you can use the following commands in Claude Code:

- **List all available tools:**
  ```
  /mcp tools
  ```
  This will show all tools your server exposes (from the `/tools` endpoint).

- **Call a tool directly:**
  ```
  /mcp call analyze_file_changes base_branch=main include_diff=true max_diff_lines=100
  ```
  Replace the tool name and parameters as needed. Claude will call your `/call/{tool_name}` endpoint.

- **See tool details:**
  ```
  /mcp describe analyze_file_changes
  ```
  (Shows the tool's description and parameters.)

**Note:** Make sure your API key is set in Claude's MCP server configuration if your endpoints require it.

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
- **Public**: `/`, `/health`, `/docs`, `/webhook/github`, `/.well-known/openid-configuration`, `/.well-known/oauth-authorization-server`
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
   railway variables set MCP_API_KEY=your_api_key  # Generate a secure random key
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

**MIT License** – Use freely, but please attribute.

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
