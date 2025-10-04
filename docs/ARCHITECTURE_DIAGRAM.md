# 🏗️ Unified main.py Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Unified main.py                                 │
│                   (Single File, Multiple Modes)                         │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
           ┌────────────┐  ┌─────────────┐  ┌──────────────┐
           │  CLI Mode  │  │   API Mode  │  │  MCP Server  │
           │  (default) │  │  (--api)    │  │  (separate)  │
           └────────────┘  └─────────────┘  └──────────────┘
```

## Detailed Architecture

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                            main.py (1000+ lines)                          ║
╚═══════════════════════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────────────────────┐
│ 1. ContentExtractor Class                                                │
├───────────────────────────────────────────────────────────────────────────┤
│   ├── extract_content(url) → Dict                                        │
│   │   └── Returns: {url, title, text, headings, code_blocks, metadata}  │
│   ├── _extract_title() → str                                             │
│   ├── _extract_headings() → List[Dict]                                   │
│   ├── _extract_code_blocks() → List[Dict]                                │
│   └── _clean_text() → str                                                │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│ 2. RAGExporter Class                                                      │
├───────────────────────────────────────────────────────────────────────────┤
│   ├── save_jsonl(filename) → int                                         │
│   │   └── Output: JSONL for vector databases                             │
│   ├── save_markdown(output_dir) → int                                    │
│   │   └── Output: Markdown files with frontmatter                        │
│   ├── save_enhanced_json(filename) → Dict                                │
│   │   └── Output: JSON with relationships                                │
│   └── export_all(base_dir) → Dict                                        │
│       └── Exports all three formats                                      │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│ 3. DatadogDocsScraper Class                                               │
├───────────────────────────────────────────────────────────────────────────┤
│   ├── scrape_recursive(url, depth=0) → None                              │
│   │   └── Recursive link discovery                                       │
│   ├── normalize_url(url) → str                                           │
│   │   └── URL deduplication                                              │
│   ├── save_results() → None                                              │
│   │   └── Save to standard formats                                       │
│   └── State:                                                              │
│       ├── visited: Set[str]                                               │
│       ├── links_tree: DefaultDict[str, List]                              │
│       └── is_scraping: bool                                               │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│ 4. FastAPI Application                                                    │
├───────────────────────────────────────────────────────────────────────────┤
│   ├── GET /                  → Welcome message                            │
│   ├── GET /health            → Health check                               │
│   ├── POST /scrape           → Trigger scraping (background)              │
│   ├── GET /status            → Scraping status                            │
│   ├── GET /results           → JSON results                               │
│   ├── GET /results/json      → Download JSON file                         │
│   ├── POST /webhook          → n8n webhook integration                    │
│   └── GET /export/rag/{fmt}  → RAG format export                          │
│       ├── /export/rag/jsonl                                               │
│       ├── /export/rag/markdown                                            │
│       ├── /export/rag/json                                                │
│       └── /export/rag/all                                                 │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│ 5. main() Function - Unified CLI Entry Point                             │
├───────────────────────────────────────────────────────────────────────────┤
│   ├── Argument Parser                                                     │
│   │   ├── --api                → API server mode                          │
│   │   ├── --extract-content    → Content extraction mode                 │
│   │   ├── --export-rag FORMAT  → RAG export mode                          │
│   │   ├── --max-depth INT      → Scraping depth                          │
│   │   ├── --delay FLOAT        → Request delay                           │
│   │   ├── --output-dir PATH    → Output directory                        │
│   │   └── --port/--host        → API server config                       │
│   │                                                                        │
│   ├── Mode Execution                                                      │
│   │   ├── if args.api:         → run_api_server()                        │
│   │   ├── elif args.extract:   → scrape + extract + save                 │
│   │   ├── elif args.export:    → export RAG formats                      │
│   │   └── else:                → default CLI scraping                    │
│   │                                                                        │
│   └── Environment Override                                                │
│       ├── MAX_DEPTH → args.max_depth                                      │
│       ├── DELAY → args.delay                                              │
│       └── PORT/HOST → API config                                          │
└───────────────────────────────────────────────────────────────────────────┘
```

## Mode Flow Diagrams

### CLI Scraping Mode (Default)

```
User Command: python main.py --max-depth 3 --delay 1.0

    │
    ▼
┌─────────────────┐
│ Parse Arguments │
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│ Create Scraper       │
│ (DatadogDocsScraper) │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ scrape_recursive()   │
│ - Depth: 3           │
│ - Delay: 1.0s        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ save_results()       │
│ - all_links.txt      │
│ - links_detailed.txt │
│ - links.json         │
│ - tree_structure.txt │
└──────────────────────┘
```

### Content Extraction Mode

```
User Command: python main.py --extract-content --max-depth 2

    │
    ▼
┌─────────────────┐
│ Parse Arguments │
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│ Create Scraper +     │
│ ContentExtractor     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ scrape_recursive()   │
│ - Collect URLs       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ For each URL:        │
│   extract_content()  │
│   - Title            │
│   - Text             │
│   - Headings         │
│   - Code blocks      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Save to JSON         │
│ output/content/      │
│   extracted_content. │
│   json               │
└──────────────────────┘
```

### RAG Export Mode

```
User Command: python main.py --export-rag all

    │
    ▼
┌─────────────────┐
│ Parse Arguments │
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│ Check for existing   │
│ scraped data         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Create Scraper +     │
│ RAGExporter          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ export_all()         │
├──────────────────────┤
│ ├─ save_jsonl()      │
│ ├─ save_markdown()   │
│ └─ save_enhanced_    │
│    json()            │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Output:              │
│ - datadog_rag.jsonl  │
│ - datadog_markdown/  │
│ - datadog_rag_       │
│   enhanced.json      │
└──────────────────────┘
```

### API Server Mode

```
User Command: python main.py --api --port 8000

    │
    ▼
┌─────────────────┐
│ Parse Arguments │
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│ run_api_server()     │
│ - Host: 0.0.0.0      │
│ - Port: 8000         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────┐
│ FastAPI Server Running           │
├──────────────────────────────────┤
│ Endpoints:                       │
│ ├─ GET /health                   │
│ ├─ POST /scrape                  │
│ ├─ GET /status                   │
│ ├─ GET /results                  │
│ ├─ POST /webhook                 │
│ └─ GET /export/rag/{format}      │
└──────────────────────────────────┘
           │
           ▼
┌──────────────────────┐
│ Listen for requests  │
│ Process in           │
│ background tasks     │
└──────────────────────┘
```

### Combined Mode

```
User Command: python main.py --max-depth 3 --extract-content --export-rag all

    │
    ▼
┌─────────────────┐
│ Parse Arguments │
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│ STAGE 1: Scrape      │
│ scrape_recursive()   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ STAGE 2: Extract     │
│ extract_content()    │
│ for each URL         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ STAGE 3: Export      │
│ export_all()         │
│ - JSONL              │
│ - Markdown           │
│ - JSON               │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ COMPLETE             │
│ All outputs saved    │
└──────────────────────┘
```

## Data Flow

```
                        ┌──────────────────────┐
                        │  Datadog Docs        │
                        │  https://docs.       │
                        │  datadoghq.com/      │
                        └──────────┬───────────┘
                                   │
                                   │ HTTP GET
                                   ▼
                        ┌──────────────────────┐
                        │  DatadogDocsScraper  │
                        │  - Recursive crawl   │
                        │  - URL normalization │
                        │  - Tree building     │
                        └──────────┬───────────┘
                                   │
                ┌──────────────────┼──────────────────┐
                │                  │                  │
                ▼                  ▼                  ▼
     ┌─────────────────┐ ┌─────────────────┐ ┌──────────────────┐
     │ Standard Output │ │ Content Extract │ │  RAG Export      │
     ├─────────────────┤ ├─────────────────┤ ├──────────────────┤
     │ - all_links.txt │ │ ContentExtractor│ │ RAGExporter      │
     │ - detailed.txt  │ │ ├─ HTML parse   │ │ ├─ JSONL         │
     │ - links.json    │ │ ├─ Text extract │ │ ├─ Markdown      │
     │ - tree.txt      │ │ ├─ Code blocks  │ │ └─ Enhanced JSON │
     └─────────────────┘ │ └─ Metadata     │ └──────────────────┘
                         └─────────────────┘
```

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Environment                       │
└─────────────────────────────────────────────────────────────────┘

┌───────────────────┐   ┌───────────────────┐   ┌───────────────┐
│ datadog-scraper   │   │ datadog-mcp-      │   │ n8n           │
│ (main.py --api)   │◄──┤ server            │◄──┤ (workflows)   │
│ Port: 8000        │   │ Port: 8001        │   │ Port: 5678    │
└─────────┬─────────┘   └───────────────────┘   └───────────────┘
          │
          │ HTTP REST API
          │
┌─────────▼──────────────────────────────────────────────────────┐
│ API Endpoints                                                   │
├─────────────────────────────────────────────────────────────────┤
│ GET  /health              → Health check                        │
│ POST /scrape              → Start scraping (background)         │
│ GET  /status              → Check progress                      │
│ GET  /results             → Get JSON data                       │
│ POST /webhook             → n8n trigger                         │
│ GET  /export/rag/{format} → Export RAG formats                  │
└─────────────────────────────────────────────────────────────────┘
```

## File System Layout

```
datadog_scraper/
├── main.py ⭐                    # Unified application
│   ├── ContentExtractor          # Full content extraction
│   ├── RAGExporter               # Multi-format export
│   ├── DatadogDocsScraper        # Core scraper
│   ├── FastAPI app               # REST API
│   └── main() function           # CLI entry point
│
├── datadog_mcp_server.py         # MCP protocol server
├── docker-compose.yml            # Container orchestration
├── Dockerfile                    # Container image
├── start.sh                      # Convenience wrapper
├── docker-deploy.sh              # Docker management
│
├── output/                       # Generated outputs
│   ├── content/
│   │   └── extracted_content.json
│   ├── datadog_markdown/
│   │   ├── integrations/
│   │   ├── metrics/
│   │   └── ...
│   ├── datadog_rag.jsonl
│   └── datadog_rag_enhanced.json
│
├── n8n-workflows/                # Workflow templates
│   ├── mcp-basic-workflow.json
│   └── results-processing-workflow.json
│
└── Documentation/
    ├── README.md
    ├── RAG_GUIDE.md
    ├── RAG_QUICKSTART.md
    ├── CONTENT_SCRAPING_GUIDE.md
    ├── CONSOLIDATION_COMPLETE.md
    ├── UNIFIED_MAIN_SUMMARY.md
    ├── FINAL_SUMMARY.md
    ├── TESTING_CHECKLIST.md
    └── .github/copilot-instructions.md
```

## Decision Tree

```
                    Start: python main.py [options]
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │ Parse CLI Arguments    │
                    └────────────┬───────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
        ┌──────────┐      ┌───────────┐     ┌──────────────┐
        │ --api?   │      │ --extract │     │ --export-rag │
        └─────┬────┘      │ -content? │     └──────┬───────┘
              │           └─────┬─────┘            │
              │ Yes             │ Yes              │ Yes
              ▼                 ▼                  ▼
     ┌─────────────────┐ ┌──────────────┐  ┌──────────────┐
     │ Run FastAPI     │ │ Scrape +     │  │ Export RAG   │
     │ Server          │ │ Extract      │  │ Formats      │
     │ - Webhooks      │ │ - Full       │  │ - JSONL      │
     │ - Background    │ │   Content    │  │ - Markdown   │
     │   Tasks         │ │ - Save JSON  │  │ - JSON       │
     └─────────────────┘ └──────────────┘  └──────────────┘
              │
              │ No (default)
              ▼
     ┌─────────────────┐
     │ CLI Scraping    │
     │ - Discover URLs │
     │ - Build Tree    │
     │ - Save Files    │
     └─────────────────┘
```

## Summary

```
┌──────────────────────────────────────────────────────────────┐
│            Unified main.py - One File, Four Modes            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Mode 1: CLI Scraping     → URL discovery + tree mapping    │
│  Mode 2: Content Extract  → Full page content extraction    │
│  Mode 3: RAG Export       → Multi-format export             │
│  Mode 4: API Server       → REST API with webhooks          │
│                                                              │
│  Combined: All modes can work together in one command!      │
│                                                              │
│  Architecture:                                               │
│  - 5 classes: ContentExtractor, RAGExporter,                │
│               DatadogDocsScraper, FastAPI app, main()       │
│  - 1000+ lines of integrated code                           │
│  - Environment variable support                             │
│  - Docker-ready deployment                                  │
│  - Comprehensive documentation                              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```
