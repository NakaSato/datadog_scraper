# Datadog Documentation Scraper with n8n Integration

A Python web scraper for Datadog's documentation that can be easily integrated with [n8n](https://n8n.io/) workflows for automation.

## Features

- 🔗 **Recursive Link Scraping**: Extracts all links from Datadog documentation up to a specified depth
- 🚀 **REST API**: FastAPI-based API server for easy integration
- 🤖 **n8n Integration**: Webhook endpoints for workflow automation
- 💾 **Multiple Output Formats**: JSON, categorized text files, and tree structure
- ⚡ **Background Processing**: Non-blocking scraping for better performance
- 🎛️ **Configurable**: Adjustable depth, delays, and output options

## Quick Start

### Prerequisites

- Python 3.12+
- Internet connection for scraping

### Installation

1. **Clone and setup:**
```bash
git clone <your-repo>
cd datadog-scraper
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
# OR using uv (recommended)
uv add -r requirements.txt
```

### Usage

#### CLI Mode (Original)
```bash
# Basic usage
python main.py

# With custom settings
python main.py --max-depth 3 --delay 1.0

# Using the startup script
chmod +x start.sh
./start.sh --max-depth 2 --delay 0.5
```

## Docker Deployment

The scraper includes Docker support for easy deployment and integration with n8n.

### Quick Start with Docker

1. **Build and run:**
```bash
# Make deployment script executable
chmod +x docker-deploy.sh

# Build and start the service
./docker-deploy.sh build
./docker-deploy.sh up
```

2. **Access the API:**
   - API Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`
   - Trigger Scraping: `POST http://localhost:8000/scrape`

3. **View logs:**
```bash
./docker-deploy.sh logs -f
```

4. **Stop the service:**
```bash
./docker-deploy.sh down
```

### Docker Configuration

#### Environment Variables
Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

Key environment variables:
- `MAX_DEPTH`: Scraping depth (default: 2)
- `DELAY`: Delay between requests in seconds (default: 0.5)
- `PORT`: API server port (default: 8000)
- `SAVE_RESULTS`: Whether to save files (default: true)

#### Volume Mounts
- `./output`: Stores scraping results and files
- `./results`: Alternative mount point for results

### n8n Integration with Docker

Start both services together:

```bash
# Start scraper with n8n
./docker-deploy.sh n8n
```

This creates a `docker-compose.n8n.yml` file and starts:
- **Scraper API**: `http://localhost:8000`
- **n8n Interface**: `http://localhost:5678`

### Production Deployment

#### Docker Compose
Use the included `docker-compose.yml` for production:

```bash
# Start with custom configuration
MAX_DEPTH=3 PORT=8080 docker-compose up -d

# Or use environment file
docker-compose --env-file .env up -d
```

#### Manual Docker Commands
```bash
# Build the image
docker build -t datadog-scraper .

# Run the container
docker run -d \
  --name datadog-scraper \
  -p 8000:8000 \
  -e MAX_DEPTH=2 \
  -e DELAY=0.5 \
  -v $(pwd)/output:/app/output \
  datadog-scraper

# View logs
docker logs -f datadog-scraper

# Stop and remove
docker stop datadog-scraper
docker rm datadog-scraper
```

### Health Monitoring

The Docker container includes health checks:

```bash
# Check health status
curl http://localhost:8000/health

# Docker health check
docker inspect datadog-scraper | jq '.[0].State.Health.Status'
```

### Troubleshooting Docker Issues

1. **Port conflicts:**
   ```bash
   # Use different port
   PORT=8080 ./docker-deploy.sh up
   ```

2. **Build fails:**
   ```bash
   # Clean and rebuild
   ./docker-deploy.sh clean
   ./docker-deploy.sh build
   ```

3. **Permission issues:**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER output/ results/
   ```

4. **n8n connection issues:**
   - Ensure both services are on the same Docker network
   - Check firewall settings
   - Verify service URLs in n8n workflows

### Docker Commands Reference

```bash
# Service management
./docker-deploy.sh up          # Start service
./docker-deploy.sh down        # Stop service
./docker-deploy.sh restart     # Restart service
./docker-deploy.sh status      # Show status

# Monitoring
./docker-deploy.sh logs        # Show all logs
./docker-deploy.sh logs -f     # Follow logs
./docker-deploy.sh logs scraper # Show only scraper logs

# Maintenance
./docker-deploy.sh build       # Rebuild image
./docker-deploy.sh clean       # Remove everything
./docker-deploy.sh n8n         # Start with n8n
```

### n8n Workflow Integration with Docker

When both services run in Docker, update your n8n workflows:

```json
{
  "parameters": {
    "method": "POST",
    "url": "http://datadog-scraper:8000/scrape",
    "bodyParameters": {
      "max_depth": 2,
      "delay": 0.5
    }
  }
}
```

### n8n Workflow Integration with Docker

When both services run in Docker, update your n8n workflows:

```json
{
  "parameters": {
    "method": "POST",
    "url": "http://datadog-scraper:8000/scrape",
    "bodyParameters": {
      "max_depth": 2,
      "delay": 0.5
    }
  }
}
```

The scraper service is available at `datadog-scraper:8000` from within the n8n container.

## MCP Server Integration

The Datadog scraper includes an MCP (Model Context Protocol) server for advanced n8n integration.

### MCP Server Features

- **🔧 Tool-Based Interface**: 6 specialized tools for different operations
- **📊 Resource Access**: Real-time status and results via MCP resources
- **🌐 Protocol Compliance**: Full MCP protocol implementation
- **⚡ Async Operations**: Non-blocking operations for better performance

### Available MCP Tools

1. **`scrape_datadog_docs`** - Initiate documentation scraping
2. **`get_scraping_status`** - Check current scraping progress
3. **`get_scraping_results`** - Retrieve results in multiple formats
4. **`search_documentation`** - Search through scraped content
5. **`get_documentation_tree`** - Get hierarchical structure
6. **`export_scraping_data`** - Export data in JSON, CSV, Markdown, HTML

### MCP Server Setup

#### Standalone MCP Server
```bash
# Install MCP dependencies
pip install mcp

# Start MCP server
python datadog_mcp_server.py --port 8001
```

#### Docker Deployment
```bash
# Start all services including MCP server
docker-compose --profile mcp up -d

# Or start with n8n
docker-compose --profile n8n up -d
```

### n8n MCP Integration

#### Configure MCP Server in n8n

1. **Open n8n Settings** → **MCP Servers**
2. **Add Server** with configuration:
```json
{
  "name": "datadog-scraper",
  "url": "http://localhost:8001",
  "enabled": true
}
```

3. **Test Connection** in n8n MCP settings

#### Use MCP Tools in Workflows

```json
{
  "parameters": {
    "tool": "scrape_datadog_docs",
    "max_depth": 2,
    "delay": 0.5
  },
  "id": "mcp-scraper",
  "name": "MCP Datadog Scraper",
  "type": "@n8n/n8n-nodes-langchain.mcpTool"
}
```

### MCP Workflow Examples

#### Basic MCP Workflow (`mcp-basic-workflow.json`)
```json
{
  "nodes": [
    {
      "parameters": {
        "tool": "scrape_datadog_docs",
        "max_depth": 2
      },
      "type": "@n8n/n8n-nodes-langchain.mcpTool"
    }
  ]
}
```

#### Advanced MCP Workflow (`mcp-advanced-workflow.json`)
```json
{
  "nodes": [
    {
      "parameters": {
        "tool": "scrape_datadog_docs"
      },
      "type": "@n8n/n8n-nodes-langchain.mcpTool"
    },
    {
      "parameters": {
        "tool": "get_scraping_results",
        "format": "summary"
      },
      "type": "@n8n/n8n-nodes-langchain.mcpTool"
    },
    {
      "parameters": {
        "tool": "export_scraping_data",
        "format": "markdown"
      },
      "type": "@n8n/n8n-nodes-langchain.mcpTool"
    }
  ]
}
```

### MCP Resources

Access real-time data via MCP resources:

- **`datadog://scraping-status`** - Current scraping status
- **`datadog://latest-results`** - Most recent results
- **`datadog://documentation-tree`** - Hierarchical structure

### Environment Variables

```bash
# MCP Server Configuration
SCRAPER_URL=http://localhost:8000
MCP_SERVER_PORT=8001
LOG_LEVEL=INFO

# n8n MCP Configuration
MCP_SERVERS_CONFIG=/data/mcp-servers.json
```

### Troubleshooting MCP Integration

1. **Connection Issues**:
   - Verify MCP server is running on port 8001
   - Check network connectivity between n8n and MCP server
   - Ensure proper Docker networking for containerized deployment

2. **Tool Execution Failures**:
   - Check MCP server logs for detailed error messages
   - Verify scraper service is accessible and healthy
   - Confirm tool parameters match expected schema

3. **Resource Access Problems**:
   - Ensure MCP resources are properly registered
   - Check resource URIs are correctly formatted
   - Verify resource data is available

### Production MCP Deployment

For production environments:

1. **Secure MCP Server**:
   ```bash
   # Use authentication if needed
   MCP_AUTH_TOKEN=your-secret-token
   ```

2. **Health Monitoring**:
   ```bash
   # MCP server health endpoint
   curl http://localhost:8001/health
   ```

3. **Logging Configuration**:
   ```bash
   LOG_LEVEL=DEBUG  # For detailed debugging
   LOG_FILE=/app/logs/mcp-server.log
   ```

### MCP vs HTTP API

| Feature | MCP Server | HTTP API |
|---------|------------|----------|
| **Protocol** | MCP Protocol | REST/HTTP |
| **n8n Integration** | Native MCP Tools | HTTP Request Nodes |
| **Type Safety** | Schema-validated | Manual validation |
| **Resources** | Built-in resource access | Custom endpoints |
| **Real-time** | Event-driven updates | Polling required |
| **Complexity** | Higher setup complexity | Simpler implementation |

Choose **MCP Server** for:
- Native n8n integration
- Type-safe tool execution
- Real-time resource access
- Advanced workflow capabilities

Choose **HTTP API** for:
- Simple integrations
- Custom authentication
- Existing HTTP-based workflows
- Lower complexity requirements

Ready-to-use n8n workflow templates are provided for different integration scenarios.

### Available Templates

1. **Basic Trigger Workflow** (`basic-trigger-workflow.json`)
   - Simple webhook-triggered scraping
   - Perfect for manual testing and basic automation

2. **Scheduled Scraping Workflow** (`scheduled-scraping-workflow.json`)
   - Automated weekly scraping with cron scheduling
   - Ideal for regular documentation monitoring

3. **Results Processing Workflow** (`results-processing-workflow.json`)
   - Process scraping results and send notifications
   - Great for analysis and alerting

4. **Complete Automation Workflow** (`complete-automation-workflow.json`)
   - Full end-to-end automation with notifications
   - Production-ready with comprehensive error handling

5. **Docker Integration Workflow** (`docker-integration-workflow.json`)
   - Optimized for Docker deployment
   - Uses container networking for service communication

### Quick Template Import

```bash
# Make import script executable
chmod +x import-n8n-workflows.sh

# List available workflows
./import-n8n-workflows.sh list

# Import specific workflow
./import-n8n-workflows.sh basic-trigger

# Import all workflows
./import-n8n-workflows.sh import-all
```

### Template Configuration

#### Environment Variables
Set these in your n8n environment or workflow:

```bash
SCRAPER_URL=http://localhost:8000  # Your scraper service URL
MAX_DEPTH=2                        # Scraping depth
DELAY=0.5                         # Delay between requests
SLACK_WEBHOOK_URL=https://hooks.slack.com/...  # For notifications
```

#### Import Steps

1. **Open n8n** in your browser
2. **Go to workflow canvas**
3. **Click menu (≡)** → **"Import from File"**
4. **Select the workflow JSON file**
5. **Update environment variables** to match your setup
6. **Configure notification webhooks** (optional)
7. **Test the workflow** manually
8. **Activate the workflow** for automated execution

### Template Customization

#### Basic Trigger Template
```json
{
  "parameters": {
    "method": "POST",
    "url": "{{ $env.SCRAPER_URL }}/webhook",
    "bodyParameters": {
      "action": "start_scraping"
    }
  }
}
```

#### Scheduled Template
```json
{
  "parameters": {
    "rule": "cron",
    "cronExpression": "0 9 * * 1"  // Every Monday at 9 AM
  }
}
```

#### Notification Template
```json
{
  "parameters": {
    "webhookUrl": "{{ $env.SLACK_WEBHOOK_URL }}",
    "text": "Scraping completed: {{ $json.total_links }} links found"
  }
}
```

### Testing Templates

1. **Start your scraper service**
2. **Import the workflow** into n8n
3. **Update environment variables** in n8n
4. **Trigger manually** to test
5. **Check execution logs** in n8n
6. **Verify results** in scraper output files

### Production Deployment

For production use:

1. **Set up environment variables** in n8n
2. **Configure proper error handling**
3. **Add logging and monitoring**
4. **Set up notifications** for failures
5. **Schedule workflows** for your needs

### Troubleshooting Templates

**Common Issues:**

1. **Connection failures**: Check SCRAPER_URL environment variable
2. **Import errors**: Ensure valid JSON format
3. **Execution failures**: Check n8n execution logs
4. **Notification failures**: Verify webhook URLs

**Debug Tips:**

- Use n8n's execution history to debug issues
- Check the scraper service health endpoint
- Verify network connectivity between services
- Test individual nodes before full workflow execution

### Advanced Template Features

#### Error Handling
Templates include basic error handling. For production:
- Add retry logic for failed requests
- Implement proper error notifications
- Use conditional logic for different scenarios

#### Data Processing
- Transform scraping results
- Filter and categorize links
- Generate reports and summaries

#### Integration Options
- Slack/Discord notifications
- Email alerts
- Database storage
- File exports
- Dashboard updates

### Key Endpoints

- `GET /` - Root endpoint with API info
- `GET /health` - Health check for monitoring
- `POST /scrape` - Trigger scraping process
- `GET /status` - Check scraping status
- `GET /results` - Get scraping results as JSON
- `GET /results/json` - Download results as JSON file
- `POST /webhook` - Webhook endpoint for n8n integration

## n8n Integration

This scraper is designed to work seamlessly with n8n workflows. Here are several integration patterns:

### 1. Webhook Trigger Integration

Create an n8n workflow that triggers scraping via webhook:

```json
{
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "webhook",
        "responseMode": "responseNode",
        "options": {}
      },
      "id": "webhook-trigger",
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://your-server:8000/webhook",
        "bodyParameters": {
          "action": "start_scraping"
        },
        "options": {}
      },
      "id": "http-request",
      "name": "Trigger Scraping",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [460, 300]
    }
  ],
  "connections": {
    "Webhook Trigger": {
      "main": [
        [
          {
            "node": "Trigger Scraping",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

### 2. Scheduled Scraping Workflow

Set up automated scraping on a schedule:

```json
{
  "nodes": [
    {
      "parameters": {
        "rule": "cron",
        "cronExpression": "0 9 * * 1"
      },
      "id": "schedule-trigger",
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://your-server:8000/scrape",
        "bodyParameters": {
          "max_depth": 2,
          "delay": 0.5,
          "save_results": true
        }
      },
      "id": "start-scraping",
      "name": "Start Scraping",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [460, 300]
    }
  ]
}
```

### 3. Results Processing Workflow

Process scraping results and send notifications:

```json
{
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "webhook",
        "responseMode": "responseNode"
      },
      "id": "webhook",
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://your-server:8000/webhook",
        "bodyParameters": {
          "action": "get_results"
        }
      },
      "id": "get-results",
      "name": "Get Results",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "values": {
          "string": [
            {
              "name": "message",
              "value": "={{ $json.total_links }} links scraped from Datadog docs"
            }
          ]
        }
      },
      "id": "prepare-notification",
      "name": "Prepare Notification",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3.3,
      "position": [680, 300]
    }
  ]
}
```

### 4. Docker Integration

For production deployment, you can containerize the scraper:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["python", "main.py", "--api", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t datadog-scraper .
docker run -p 8000:8000 datadog-scraper
```

## Configuration

### Scraping Parameters

- **max_depth**: Maximum recursion depth (default: 2)
  - 1 = only immediate links
  - 2 = links + sublinks
  - 3+ = deeper crawling (use responsibly)

- **delay**: Seconds between requests (default: 0.5)
  - Be respectful to servers
  - Increase for larger depths

### API Configuration

The API server accepts these parameters:

```json
{
  "max_depth": 2,
  "delay": 0.5,
  "save_results": true
}
```

## Output Files

The scraper generates multiple output formats:

1. **`datadog_all_links.txt`**: Simple list of all URLs
2. **`datadog_links_detailed.txt`**: Categorized links by section
3. **`datadog_links.json`**: Complete JSON with tree structure
4. **`datadog_tree_structure.txt`**: Visual tree representation

## Monitoring and Health Checks

- **Health endpoint**: `GET /health` - Check if service is running
- **Status endpoint**: `GET /status` - Check scraping progress
- **Background processing**: Scraping runs in background threads

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Port conflicts**: Change the API port
   ```bash
   python main.py --api --port 8080
   ```

3. **Scraping fails**: Check your internet connection and try increasing delay
   ```bash
   python main.py --delay 2.0
   ```

4. **n8n connection issues**: Ensure the scraper server is accessible from n8n
   - Check firewall settings
   - Verify URL in n8n workflows

### Logs

The scraper outputs progress information to the console. For API mode, check the server logs for detailed information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

---

**Note**: This scraper is designed for educational and legitimate use cases. Always respect `robots.txt` files and website terms of service when scraping.