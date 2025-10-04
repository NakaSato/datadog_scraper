# 🎉 Unified main.py - Complete Integration Summary

## ✅ Mission Accomplished

All separate scripts have been successfully **consolidated into a single `main.py`** file with full multi-mode capabilities!

## 📦 What's Integrated

### Previously Separate Files (Now Integrated)
1. ~~`scrape_with_content.py`~~ → Integrated as `ContentExtractor` class
2. ~~`rag_exporter.py`~~ → Integrated as `RAGExporter` class
3. ~~`examples_rag.py`~~ → Functionality built into CLI modes
4. ~~`run_content_scraper.sh`~~ → Replaced by `python main.py --extract-content`

### Now in One File (`main.py`)
- ✅ **DatadogDocsScraper** - Core scraping engine
- ✅ **ContentExtractor** - Full page content extraction
- ✅ **RAGExporter** - Multi-format RAG exports
- ✅ **FastAPI Server** - REST API with webhooks
- ✅ **Unified CLI** - Single entry point with all modes

## 🚀 Quick Start Guide

### Installation
```bash
# Clone and setup
cd datadog_scraper
uv sync  # or pip install -r requirements.txt

# Verify installation
python main.py --help
```

### Basic Usage

#### 1. Simple Scraping
```bash
python main.py
```
**Output**: `datadog_all_links.txt`, `datadog_links.json`, `datadog_tree_structure.txt`

#### 2. Deep Scraping
```bash
python main.py --max-depth 3 --delay 1.0
```

#### 3. Full Content Extraction
```bash
python main.py --extract-content --max-depth 2
```
**Output**: All standard files + `output/content/extracted_content.json` with full page content

#### 4. Export for RAG/Vector Databases
```bash
python main.py --export-rag all
```
**Output**: 
- `output/datadog_rag.jsonl` (for Pinecone, Weaviate, ChromaDB)
- `output/datadog_markdown/` (for LangChain, LlamaIndex)
- `output/datadog_rag_enhanced.json` (with relationships)

#### 5. API Server
```bash
python main.py --api --port 8000
```
**Access**:
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

#### 6. All-in-One Pipeline
```bash
python main.py --max-depth 3 --extract-content --export-rag all --delay 1.0
```
**Does**:
1. Scrapes Datadog docs (depth 3)
2. Extracts full content from each page
3. Exports to all RAG formats
4. Saves standard outputs

## 📋 Mode Reference

| Mode | Flag | What It Does |
|------|------|--------------|
| **CLI** (default) | - | Scrapes URLs, builds tree structure |
| **Content Extraction** | `--extract-content` | Extracts full HTML content, code blocks, headings |
| **RAG Export** | `--export-rag {format}` | Exports in RAG-optimized formats |
| **API Server** | `--api` | Runs FastAPI server for webhooks |

## 🎯 Common Use Cases

### Use Case 1: Build Vector Database
```bash
# Step 1: Scrape with content
python main.py --extract-content --max-depth 3

# Step 2: Export to JSONL
python main.py --export-rag jsonl

# Step 3: Load into Pinecone/Weaviate/ChromaDB
# Use output/datadog_rag.jsonl
```

### Use Case 2: LangChain/LlamaIndex Integration
```bash
# Export markdown files with frontmatter
python main.py --export-rag markdown

# Use output/datadog_markdown/ with LangChain DirectoryLoader
```

### Use Case 3: n8n Automation
```bash
# Terminal 1: Start API server
python main.py --api

# Terminal 2: Trigger via webhook
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"action": "start_scraping"}'

# Check status
curl http://localhost:8000/status

# Get results
curl http://localhost:8000/results
```

### Use Case 4: Quick Analysis
```bash
# Shallow scrape for quick overview
python main.py --max-depth 1

# Check how many pages found
wc -l datadog_all_links.txt
```

## 📁 Output Files Reference

### Standard CLI Output
```
datadog_all_links.txt           # Plain list of URLs
datadog_links_detailed.txt      # URLs with depth markers
datadog_links.json              # Full tree structure (JSON)
datadog_tree_structure.txt      # Visual ASCII tree
```

### Content Extraction Output
```
output/
  content/
    extracted_content.json      # Array of {url, title, text, headings, code_blocks, metadata}
```

### RAG Export Outputs

#### JSONL (Vector Databases)
```
output/datadog_rag.jsonl
```
Format:
```jsonl
{"id": "datadog_doc_1", "url": "...", "title": "...", "content": "...", "metadata": {...}}
{"id": "datadog_doc_2", "url": "...", "title": "...", "content": "...", "metadata": {...}}
```

#### Markdown (LangChain/LlamaIndex)
```
output/datadog_markdown/
  integrations/
    aws.md
    azure.md
    ...
  metrics/
    custom-metrics.md
    ...
```

Each file has frontmatter:
```markdown
---
url: https://docs.datadoghq.com/integrations/aws
category: integrations
depth: 1
title: AWS Integration
parent_url: https://docs.datadoghq.com/
scraped_at: 2024-01-15T10:30:00
---

# AWS Integration
...
```

#### Enhanced JSON (Relationships)
```json
{
  "documents": [
    {
      "id": "datadog_doc_1",
      "url": "...",
      "title": "...",
      "metadata": {
        "category": "integrations",
        "depth": 1,
        "parent_url": "...",
        "child_urls": [...],
        "child_count": 5
      }
    }
  ],
  "metadata": {
    "total_documents": 1234,
    "categories": {"integrations": 300, "metrics": 200},
    "base_url": "https://docs.datadoghq.com/"
  }
}
```

## 🐳 Docker Deployment

The unified main.py works perfectly with Docker:

```bash
# Quick start
./docker-deploy.sh build
./docker-deploy.sh up

# With n8n integration
./docker-deploy.sh n8n

# View logs
./docker-deploy.sh logs -f

# Stop all
./docker-deploy.sh down
```

Environment variables in `docker-compose.yml`:
```yaml
environment:
  - MAX_DEPTH=3
  - DELAY=1.0
  - PORT=8000
  - HOST=0.0.0.0
```

## 🔧 Configuration

### Via Command Line
```bash
python main.py \
  --max-depth 3 \
  --delay 1.0 \
  --output-dir ./my_output \
  --export-rag all
```

### Via Environment Variables
```bash
export MAX_DEPTH=3
export DELAY=1.0
export OUTPUT_DIR=./my_output

python main.py --export-rag all
```

### Precedence Order
1. Command-line arguments (highest priority)
2. Environment variables
3. Defaults (lowest priority)

## 📊 API Endpoints (API Mode)

### Core Endpoints
- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

### Scraping Endpoints
- `POST /scrape` - Start scraping (background task)
  ```json
  {
    "max_depth": 3,
    "delay": 1.0,
    "save_results": true
  }
  ```
- `GET /status` - Check scraping status
- `GET /results` - Get JSON results
- `GET /results/json` - Download as file

### Webhook Endpoints (n8n Integration)
- `POST /webhook` - Webhook trigger
  ```json
  {
    "action": "start_scraping"
  }
  ```

### RAG Export Endpoints
- `GET /export/rag/jsonl` - Export JSONL format
- `GET /export/rag/markdown` - Export Markdown (zip file)
- `GET /export/rag/json` - Export enhanced JSON
- `GET /export/rag/all` - Export all formats

## 🧪 Testing the Integration

```bash
# Test 1: Help output
python main.py --help

# Test 2: Quick scrape (depth 1)
python main.py --max-depth 1

# Test 3: Content extraction
python main.py --extract-content --max-depth 1

# Test 4: RAG export
python main.py --export-rag jsonl

# Test 5: API server
python main.py --api &
sleep 2
curl http://localhost:8000/health
kill %1
```

## 🎨 Architecture Benefits

### Before (Multiple Files)
```
main.py                 # Basic scraping
scrape_with_content.py  # Content extraction
rag_exporter.py         # RAG export
examples_rag.py         # Examples
run_content_scraper.sh  # Shell wrapper
```
**Problems**: Fragmented, hard to maintain, confusing workflows

### After (Unified)
```
main.py                 # Everything!
```
**Benefits**:
- ✅ Single entry point
- ✅ Consistent interface
- ✅ Easier maintenance
- ✅ Better Docker integration
- ✅ Flexible mode combinations

## 📚 Related Documentation

- `README.md` - Project overview
- `RAG_GUIDE.md` - Complete RAG integration guide
- `RAG_QUICKSTART.md` - Quick reference for RAG formats
- `CONTENT_SCRAPING_GUIDE.md` - Content extraction details
- `CONSOLIDATION_COMPLETE.md` - Migration guide
- `.github/copilot-instructions.md` - AI coding agent guide

## 🚀 Next Steps

1. **Test the unified script**:
   ```bash
   python main.py --max-depth 1
   ```

2. **Try content extraction**:
   ```bash
   python main.py --extract-content --max-depth 1
   ```

3. **Export to RAG format**:
   ```bash
   python main.py --export-rag all
   ```

4. **Start API server**:
   ```bash
   python main.py --api
   ```

5. **Run full pipeline**:
   ```bash
   python main.py --max-depth 3 --extract-content --export-rag all
   ```

## ✨ Summary

You now have a **powerful, unified scraping tool** with:

- ✅ **One command**: `python main.py`
- ✅ **Four modes**: CLI, Content, RAG, API
- ✅ **Multiple exports**: JSONL, Markdown, JSON
- ✅ **Docker ready**: Works seamlessly in containers
- ✅ **Fully integrated**: No separate scripts needed

**Everything you need in one file!** 🎉
