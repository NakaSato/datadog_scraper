# ✅ Consolidation Complete: Unified main.py

## Overview

All functionality has been successfully consolidated into a **single `main.py` file** with multiple operational modes. You can now run everything from one script!

## 🎯 What Was Merged

### 1. **Core Scraper** (`DatadogDocsScraper`)
- Original recursive link scraping
- Tree structure mapping
- Rate limiting with configurable delay
- URL normalization and deduplication

### 2. **Content Extractor** (`ContentExtractor`)
- Full HTML content extraction
- Clean text processing
- Code block extraction with language detection
- Heading structure extraction
- Metadata enrichment

### 3. **RAG Exporter** (`RAGExporter`)
- JSONL format for vector databases (Pinecone, Weaviate, ChromaDB)
- Markdown files with frontmatter for LangChain/LlamaIndex
- Enhanced JSON with relationships and metadata
- Bulk export with `export_all()` method

### 4. **FastAPI Server**
- REST API endpoints for webhook integration
- Background task processing
- Health checks and status monitoring
- RAG export API endpoints

## 🚀 Usage Examples

### 1. CLI Scraping (Default Mode)
```bash
# Basic scraping
python main.py

# Custom depth and delay
python main.py --max-depth 3 --delay 1.0

# Save to custom directory
python main.py --max-depth 2 --output-dir ./my_scrape
```

### 2. Content Extraction Mode
```bash
# Extract full page content (not just URLs)
python main.py --extract-content --max-depth 2

# Extract with custom output directory
python main.py --extract-content --max-depth 3 --output-dir ./scraped_content
```

### 3. RAG Export Mode
```bash
# Export all RAG formats
python main.py --export-rag all

# Export specific format
python main.py --export-rag jsonl
python main.py --export-rag markdown
python main.py --export-rag json

# Export to custom directory
python main.py --export-rag all --output-dir ./rag_output
```

### 4. Combined Operations
```bash
# Scrape + Extract + Export in one command
python main.py --max-depth 3 --extract-content --export-rag all

# Scrape + Export (without content extraction)
python main.py --max-depth 2 --export-rag jsonl
```

### 5. API Server Mode
```bash
# Start API server (default port 8000)
python main.py --api

# Custom host and port
python main.py --api --host 0.0.0.0 --port 8080
```

## 📋 Complete Command-Line Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--api` | flag | False | Run as API server |
| `--extract-content` | flag | False | Extract full page content |
| `--export-rag` | choice | None | Export format: jsonl, markdown, json, all |
| `--max-depth` | int | 2 | Maximum scraping depth |
| `--delay` | float | 0.5 | Delay between requests (seconds) |
| `--output-dir` | string | output | Output directory for results |
| `--save-results` | flag | True | Save results to files |
| `--port` | int | 8000 | API server port |
| `--host` | string | 0.0.0.0 | API server host |

## 🔧 Environment Variables (Docker Support)

Override any setting via environment variables:

```bash
export MAX_DEPTH=3
export DELAY=1.0
export PORT=8080
export HOST=0.0.0.0

python main.py --api
```

## 📂 Output Structure

### CLI Mode (Default)
```
output/
  datadog_all_links.txt         # Simple list of URLs
  datadog_links_detailed.txt    # URLs with metadata
  datadog_links.json            # Full tree structure
  datadog_tree_structure.txt    # Visual tree
```

### Content Extraction Mode
```
output/
  content/
    extracted_content.json      # Full page content with metadata
  datadog_all_links.txt
  datadog_links_detailed.txt
  datadog_links.json
  datadog_tree_structure.txt
```

### RAG Export Mode
```
output/
  datadog_rag.jsonl                # JSONL for vector databases
  datadog_rag_enhanced.json        # Enhanced JSON with metadata
  datadog_markdown/                # Markdown files by category
    integrations/
      aws.md
      azure.md
      ...
    metrics/
      custom-metrics.md
      ...
```

## 🎨 API Endpoints

When running in API mode (`python main.py --api`):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message |
| `/health` | GET | Health check |
| `/scrape` | POST | Start scraping (background task) |
| `/status` | GET | Get scraping status |
| `/results` | GET | Get JSON results |
| `/results/json` | GET | Download results as file |
| `/webhook` | POST | n8n webhook integration |
| `/export/rag/jsonl` | GET | Export JSONL format |
| `/export/rag/markdown` | GET | Export Markdown (zip) |
| `/export/rag/json` | GET | Export enhanced JSON |
| `/export/rag/all` | GET | Export all formats |

## 🐳 Docker Usage

The unified main.py works seamlessly with Docker:

```bash
# Build and run
./docker-deploy.sh build
./docker-deploy.sh up

# Or with docker-compose directly
docker-compose up -d

# Check logs
./docker-deploy.sh logs -f
```

## 📊 Example Workflows

### Workflow 1: Quick Scrape
```bash
python main.py --max-depth 2
```

### Workflow 2: Deep Content Extraction
```bash
python main.py --extract-content --max-depth 3 --delay 1.0
```

### Workflow 3: Generate RAG Data for LangChain
```bash
# Step 1: Scrape
python main.py --max-depth 3

# Step 2: Export to RAG formats
python main.py --export-rag all
```

### Workflow 4: All-in-One
```bash
python main.py --max-depth 3 --extract-content --export-rag all --delay 1.0
```

### Workflow 5: API Server for n8n
```bash
python main.py --api --port 8000
```

## ✨ Key Benefits of Consolidation

1. **Single Entry Point**: No more juggling multiple scripts
2. **Consistent CLI**: Unified argument handling
3. **Easier Maintenance**: All code in one place
4. **Better Docker Integration**: One container, multiple modes
5. **Flexible Workflows**: Mix and match modes as needed
6. **Environment Variable Support**: Docker-friendly configuration

## 🧪 Testing the Unified Script

```bash
# Test CLI mode
python main.py --help

# Test quick scrape
python main.py --max-depth 1

# Test RAG export
python main.py --export-rag jsonl

# Test API mode
python main.py --api &
curl http://localhost:8000/health
```

## 📝 Migration Notes

### If you were using separate scripts:

**Old way:**
```bash
python main.py                    # Basic scraping
python scrape_with_content.py     # Content extraction
python -c "from rag_exporter import RAGExporter; ..."  # RAG export
```

**New way:**
```bash
python main.py                              # Basic scraping
python main.py --extract-content            # Content extraction
python main.py --export-rag all             # RAG export
```

## 🎉 Summary

You now have a **single, powerful `main.py`** that handles:
- ✅ CLI scraping (default)
- ✅ Content extraction (`--extract-content`)
- ✅ RAG exports (`--export-rag`)
- ✅ API server (`--api`)
- ✅ Combined workflows (all flags together)

**One script. Multiple modes. Maximum flexibility.** 🚀
