# Copilot Instructions for Datadog Scraper

## Architecture Overview

This is a **multi-mode Python application** that scrapes Datadog documentation with three distinct integration patterns:

1. **CLI Scraper** (`main.py`) - Original standalone functionality
2. **FastAPI Server** (`main.py --api`) - REST API for webhook integration
3. **MCP Server** (`datadog_mcp_server.py`) - Model Context Protocol server for advanced n8n integration

## Key Design Patterns

### Dual-Mode Application
- `main.py` serves as both CLI tool and FastAPI server based on `--api` flag
- Single `DatadogDocsScraper` class handles core scraping logic
- Global scraper instance shared between API endpoints for state management

### Background Processing Pattern
```python
# API triggers background scraping to avoid blocking
background_tasks.add_task(run_scraping, request.max_depth, request.delay, request.save_results)
```

### Multi-Format Output Strategy
- Text files: `datadog_all_links.txt`, `datadog_links_detailed.txt`, `datadog_tree_structure.txt`
- JSON: `datadog_links.json` with complete tree structure
- API endpoints serve both raw JSON and downloadable files

### Environment-First Configuration
```python
# Environment variables override CLI args consistently
env_max_depth = os.getenv('MAX_DEPTH')
if env_max_depth:
    args.max_depth = int(env_max_depth)
```

## Critical Development Workflows

### Local Development
```bash
# Use start.sh wrapper for all operations
chmod +x start.sh
./start.sh --api --port 8080           # API mode
./start.sh --max-depth 3 --delay 1.0   # CLI mode
```

### Docker Deployment
```bash
# Use docker-deploy.sh for container management
chmod +x docker-deploy.sh
./docker-deploy.sh build && ./docker-deploy.sh up
./docker-deploy.sh n8n  # Start with n8n integration
```

### MCP Server Development
```python
# MCP server runs independently, communicates via HTTP
python datadog_mcp_server.py  # Port 8001 by default
# Requires main scraper API running on port 8000
```

## Integration Architecture

### n8n Webhook Integration
- **Trigger endpoint**: `POST /webhook` with `{"action": "start_scraping"}`
- **Status checking**: `GET /status` for polling progress
- **Results retrieval**: `GET /results` for JSON or `GET /results/json` for file download

### MCP Server Tools
Six distinct tools available via MCP protocol:
- `scrape_datadog_docs` - Initiate scraping
- `get_scraping_status` - Check progress
- `get_scraping_results` - Retrieve data
- `search_documentation` - Search scraped content
- `get_documentation_tree` - Get hierarchical structure
- `export_scraping_data` - Export in multiple formats

### Service Communication
```yaml
# Docker networking pattern
networks:
  scraper-network:
    # MCP server calls scraper API via: http://datadog-scraper:8000
    # n8n calls both services via container names
```

## Project-Specific Conventions

### URL Normalization Strategy
```python
def normalize_url(self, url):
    # Removes fragments and trailing slashes for deduplication
    # Critical for preventing infinite loops in recursive scraping
```

### Rate Limiting Pattern
- Default 0.5s delay between requests
- Configurable via `--delay` or `DELAY` env var
- Always respect servers with `time.sleep(self.delay)`

### File Organization
- `/output/` - Generated scraping results
- `/results/` - Alternative output mount for Docker
- `/n8n-workflows/` - Template workflows for import

### Environment Variable Precedence
Order: CLI args → Environment variables → Defaults
```python
# Consistent pattern used throughout
args.port = int(os.getenv('PORT', args.port))
```

## Docker Compose Profiles
```yaml
profiles:
  - mcp    # Only start MCP server when needed
  - n8n    # Full n8n integration stack
```

### Health Check Strategy
- All services include health endpoints at `/health`
- Docker health checks use curl with 30s intervals
- Background process tracking via `scraper.is_scraping` flag

## Common Debugging Patterns

### API Server Issues
```bash
# Check if API is responding
curl http://localhost:8000/health
# View API documentation
curl http://localhost:8000/docs
```

### Docker Networking Problems
```bash
# Check container connectivity
docker exec -it datadog-scraper curl http://localhost:8000/health
# View container logs
./docker-deploy.sh logs -f
```

### MCP Server Integration
```python
# MCP server depends on main scraper API
self.scraper_url = os.getenv("SCRAPER_URL", "http://localhost:8000")
# Always verify scraper connectivity before MCP operations
```

## Key Files for Extension

- `main.py:DatadogDocsScraper` - Core scraping logic
- `main.py:app` - FastAPI application with webhook endpoints  
- `datadog_mcp_server.py:DatadogScraperMcpServer` - MCP protocol implementation
- `docker-compose.yml` - Multi-service orchestration with profiles
- `start.sh` / `docker-deploy.sh` - Deployment automation scripts