# Copilot Instructions for Datadog Scraper

## Architecture Overview

This is a **unified Python application** (`main.py`) that scrapes Datadog documentation with four distinct operational modes, all accessible from a single entry point:

1. **CLI Scraper** (default) - Standalone link discovery and tree mapping
2. **Content Extractor** (`--extract-content`) - Full HTML content extraction with metadata
3. **RAG Exporter** (`--export-rag`) - Multi-format export for vector databases and RAG systems
4. **FastAPI Server** (`--api`) - REST API for webhook integration and n8n automation

## Key Design Patterns

### Single-File Multi-Mode Architecture
```python
# main.py contains all functionality:
# - DatadogDocsScraper: Core scraping engine
# - ContentExtractor: Full page content extraction
# - RAGExporter: Multi-format export (JSONL, Markdown, JSON)
# - FastAPI app: REST API with webhook endpoints

# Modes selected via CLI flags:
python main.py                      # CLI scraping
python main.py --extract-content    # Content extraction
python main.py --export-rag all     # RAG export
python main.py --api                # API server
```

### Unified CLI Pattern
```python
# All modes share common options and can be combined:
parser.add_argument('--max-depth', type=int, default=2)
parser.add_argument('--delay', type=float, default=0.5)
parser.add_argument('--output-dir', type=str, default='output')

# Combined usage example:
python main.py --max-depth 3 --extract-content --export-rag all
```

### Background Processing Pattern
```python
# API triggers background scraping to avoid blocking
background_tasks.add_task(run_scraping, request.max_depth, request.delay, request.save_results)
```

### Multi-Format Output Strategy
- **Standard outputs**: `datadog_all_links.txt`, `datadog_links_detailed.txt`, `datadog_tree_structure.txt`, `datadog_links.json`
- **Content extraction**: `output/content/extracted_content.json` (full page content with metadata)
- **RAG formats**: 
  - JSONL: `output/datadog_rag.jsonl` (for vector databases)
  - Markdown: `output/datadog_markdown/` (for LangChain/LlamaIndex)
  - Enhanced JSON: `output/datadog_rag_enhanced.json` (with relationships)

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
# Use main.py directly for all operations
python main.py --help                          # Show all options
python main.py --max-depth 3                   # CLI scraping
python main.py --extract-content --max-depth 2 # Content extraction
python main.py --export-rag all                # RAG export
python main.py --api --port 8000               # API server

# Or use start.sh wrapper
chmod +x start.sh
./start.sh --api --port 8080
./start.sh --max-depth 3 --delay 1.0
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

### Operational Modes

#### 1. CLI Scraping Mode (Default)
```bash
python main.py --max-depth 3 --delay 1.0
```
- Discovers links recursively
- Builds tree structure
- Saves to text and JSON files
- No content extraction (URLs only)

#### 2. Content Extraction Mode
```bash
python main.py --extract-content --max-depth 2
```
- Scrapes links (like CLI mode)
- Extracts full HTML content from each page
- Parses code blocks, headings, metadata
- Saves to `output/content/extracted_content.json`

#### 3. RAG Export Mode
```bash
python main.py --export-rag {jsonl|markdown|json|all}
```
- Exports scraped data in RAG-optimized formats
- JSONL: One JSON document per line (vector databases)
- Markdown: Files with frontmatter (LangChain/LlamaIndex)
- JSON: Enhanced format with relationships

#### 4. API Server Mode
```bash
python main.py --api --port 8000
```
- FastAPI server with OpenAPI docs
- Webhook endpoints for n8n
- Background task processing
- Health checks and status monitoring

#### 5. Combined Mode
```bash
python main.py --max-depth 3 --extract-content --export-rag all
```
- Runs multiple modes in sequence
- Scrape → Extract → Export pipeline

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
- `/output/` - Primary output directory
  - `/content/` - Extracted page content
  - `/datadog_markdown/` - RAG markdown exports
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

### Mode Selection Issues
```bash
# Verify available modes
python main.py --help

# Test each mode individually
python main.py --max-depth 1                    # CLI
python main.py --extract-content --max-depth 1  # Content
python main.py --export-rag jsonl               # RAG
python main.py --api                            # API
```

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

## RAG Integration Patterns

### Optimal File Formats for Vector Databases
- **JSONL** (primary): One JSON document per line for streaming ingestion
  - Export: `python main.py --export-rag jsonl`
  - Use with: Pinecone, Weaviate, ChromaDB, Qdrant
  
- **Markdown**: Structured docs with frontmatter metadata for LangChain/LlamaIndex
  - Export: `python main.py --export-rag markdown`
  - Use with: LangChain DirectoryLoader, LlamaIndex SimpleDirectoryReader
  
- **Enhanced JSON**: Columnar storage with relationships and metadata
  - Export: `python main.py --export-rag json`
  - Use with: Custom processing, analytics

### Content Extraction Strategy
```python
class ContentExtractor:
    def extract_content(self, url: str) -> Dict:
        # Remove nav/header/footer
        # Extract main content with structure
        # Preserve code blocks and formatting
        # Return: {url, title, text, headings, code_blocks, metadata}
```

### Chunking Conventions
- Default: 1000 tokens per chunk, 200 token overlap
- Split on semantic boundaries (headers, sections)
- Include metadata: url, category, depth, parent_url, section

### Export Endpoints (API Mode)
```python
# API endpoints for RAG-optimized formats
GET /export/rag/jsonl      # Stream JSONL for vector DBs
GET /export/rag/markdown   # Zip of markdown files
GET /export/rag/json       # Enhanced JSON with relationships
GET /export/rag/all        # Export all formats
```

## Key Classes and Their Responsibilities

### DatadogDocsScraper
- **Purpose**: Core scraping engine
- **Key Methods**:
  - `scrape_recursive(url, depth=0)` - Recursive link discovery
  - `normalize_url(url)` - URL deduplication
  - `save_results()` - Save to standard formats
- **State**: `visited` (set), `links_tree` (dict), `is_scraping` (bool)

### ContentExtractor
- **Purpose**: Full page content extraction
- **Key Methods**:
  - `extract_content(url)` - Extract clean content
  - `_extract_code_blocks(content)` - Parse code with language detection
  - `_extract_headings(content)` - Build heading structure
- **Output**: JSON with `{url, title, text, headings, code_blocks, metadata}`

### RAGExporter
- **Purpose**: Multi-format RAG export
- **Key Methods**:
  - `save_jsonl(filename)` - Export JSONL for vector DBs
  - `save_markdown(output_dir)` - Export markdown with frontmatter
  - `save_enhanced_json(filename)` - Export with relationships
  - `export_all(base_dir)` - Export all formats
- **Dependencies**: Requires `DatadogDocsScraper` instance

### FastAPI Application
- **Purpose**: REST API for webhooks and automation
- **Endpoints**: 
  - `/scrape`, `/status`, `/results`, `/webhook`
  - `/export/rag/{format_type}`
- **Background Tasks**: Non-blocking scraping with status tracking

## Key Files for Extension

- `main.py` - **Unified application** (all functionality)
  - `DatadogDocsScraper` class (lines ~200-400)
  - `ContentExtractor` class (lines ~70-150)
  - `RAGExporter` class (lines ~150-250)
  - FastAPI app definition (lines ~500-700)
  - Unified main() function (lines ~750+)
  
- `datadog_mcp_server.py` - MCP protocol implementation
- `docker-compose.yml` - Multi-service orchestration with profiles
- `start.sh` / `docker-deploy.sh` - Deployment automation scripts

## Documentation Files
- `README.md` - Project overview and quick start
- `RAG_GUIDE.md` - Comprehensive RAG integration guide
- `RAG_QUICKSTART.md` - Quick reference for RAG formats
- `CONTENT_SCRAPING_GUIDE.md` - Content extraction details
- `CONSOLIDATION_COMPLETE.md` - Migration from separate scripts
- `UNIFIED_MAIN_SUMMARY.md` - Complete usage guide

## Migration Notes

### Previous Architecture (Deprecated)
```
main.py                 # Basic scraping only
scrape_with_content.py  # Content extraction (deprecated)
rag_exporter.py         # RAG export (deprecated)
examples_rag.py         # Examples (deprecated)
run_content_scraper.sh  # Shell wrapper (deprecated)
```

### Current Architecture (Unified)
```
main.py                 # Everything integrated!
  - CLI scraping
  - Content extraction
  - RAG export
  - API server
```

### Migration Path
**Old**: `python scrape_with_content.py --max-depth 3`  
**New**: `python main.py --extract-content --max-depth 3`

**Old**: `python -c "from rag_exporter import RAGExporter; ..."`  
**New**: `python main.py --export-rag all`

## Development Best Practices

1. **Always use main.py**: Don't create separate scripts for new features
2. **Extend existing classes**: Add methods to DatadogDocsScraper, ContentExtractor, or RAGExporter
3. **Add CLI flags**: Extend the argument parser for new modes
4. **Maintain backward compatibility**: Existing workflows should continue working
5. **Test all modes**: Verify CLI, content extraction, RAG export, and API after changes
6. **Update documentation**: Keep README.md and guide files in sync

## Testing Strategy

```bash
# Test 1: CLI mode
python main.py --max-depth 1

# Test 2: Content extraction
python main.py --extract-content --max-depth 1

# Test 3: RAG export
python main.py --export-rag jsonl

# Test 4: API server
python main.py --api &
curl http://localhost:8000/health
kill %1

# Test 5: Combined mode
python main.py --max-depth 1 --extract-content --export-rag all

# Test 6: Docker deployment
./docker-deploy.sh build && ./docker-deploy.sh up
./docker-deploy.sh down
```