# ✅ Complete: Deep Path Content Scraping with RAG Format

## 🎉 What's Been Created

I've built a complete solution to **fetch all paths from URLs with deep scraping**, **extract full content**, and **save to markdown** following the RAG_GUIDE.md specifications!

## 📁 New Files

### 1. **`scrape_with_content.py`** ⭐ Main Scraper
- Recursively scrapes Datadog docs to configurable depth
- Extracts **full page content** (not just URLs!)
- Removes navigation, headers, footers (clean content)
- Extracts code blocks with language detection
- Saves to markdown with YAML frontmatter
- Creates organized directory structure by category

### 2. **`run_content_scraper.sh`** - Quick Start Script
- Interactive wrapper for easy use
- Configurable depth and delay
- Shows summary and results

### 3. **`CONTENT_SCRAPING_GUIDE.md`** - Complete Documentation
- Step-by-step instructions
- Configuration options
- Integration examples (LangChain, ChromaDB)
- Troubleshooting guide

## 🚀 How to Run

### Simplest Way:
```bash
python3 scrape_with_content.py
```

### With Custom Settings:
```bash
# Shallow scraping (faster, for testing)
MAX_DEPTH=1 DELAY=0.5 python3 scrape_with_content.py

# Balanced (recommended)
MAX_DEPTH=2 DELAY=1.0 python3 scrape_with_content.py

# Deep scraping (comprehensive, slower)
MAX_DEPTH=3 DELAY=1.5 python3 scrape_with_content.py
```

### Using the Shell Script:
```bash
chmod +x run_content_scraper.sh
./run_content_scraper.sh 2 1.0
# (depth=2, delay=1.0s)
```

## 📊 What You Get

### Output Structure:
```
output/datadog_markdown_full/
├── INDEX.md                    # Complete navigation index
├── SUMMARY.json               # Statistics (word counts, etc.)
├── api/                       # Category-based folders
│   ├── api-overview.md
│   ├── api-authentication.md
│   └── ...
├── integrations/
│   ├── integrations-aws.md
│   ├── integrations-azure.md
│   └── ...
└── getting-started/
    └── ...
```

### Each Markdown File Contains:

```markdown
---
url: https://docs.datadoghq.com/api
title: API Documentation
category: api
depth: 1
parent_url: https://docs.datadoghq.com
word_count: 1524
scraped_at: 2025-10-05T10:30:00
source: datadog_docs
---

# API Documentation

**URL:** [https://docs.datadoghq.com/api](...)

## Table of Contents
- Section 1
- Section 2

## Content
[Full extracted page content here...]

## Code Examples

```python
# Code blocks automatically extracted
import datadog
```

---
*Extracted: 2025-10-05T10:30:00*
*Word Count: 1524*
```

## ✨ Key Features

### Content Extraction ✅
- ✅ Full page text (not just URLs)
- ✅ Headings (h1-h6) for document structure
- ✅ Code blocks with language detection
- ✅ Metadata (category, depth, parent URLs)
- ✅ Clean content (removes nav/footer/scripts)

### RAG-Optimized Format ✅
- ✅ YAML frontmatter metadata
- ✅ Markdown structure
- ✅ Table of contents
- ✅ Code sections
- ✅ Word counts and timestamps

### Organization ✅
- ✅ Category-based folders
- ✅ Safe filenames
- ✅ Complete index file
- ✅ Summary statistics

### RAG Integration Ready ✅
- ✅ LangChain DirectoryLoader compatible
- ✅ Frontmatter parsing
- ✅ Semantic chunking friendly
- ✅ Vector DB ready

## 🔌 Use With RAG Tools

### LangChain
```python
from langchain.document_loaders import DirectoryLoader

loader = DirectoryLoader(
    'output/datadog_markdown_full/',
    glob='**/*.md'
)
docs = loader.load()
# Ready for vector store!
```

### ChromaDB
```python
import chromadb
from pathlib import Path

client = chromadb.Client()
collection = client.create_collection("datadog-docs")

for md_file in Path('output/datadog_markdown_full').rglob('*.md'):
    content = md_file.read_text()
    collection.add(
        documents=[content],
        ids=[str(md_file)]
    )
```

## 📈 Comparison

| Feature | Old Scraper | New Content Scraper |
|---------|-------------|-------------------|
| URLs | ✅ Yes | ✅ Yes |
| Full Content | ❌ No | ✅ **Yes** |
| Code Blocks | ❌ No | ✅ **Yes** |
| Headings | ❌ No | ✅ **Yes** |
| Markdown | ❌ No | ✅ **Yes (RAG format)** |
| Metadata | Partial | ✅ **Complete** |
| Organization | Flat | ✅ **By Category** |
| Index | ❌ No | ✅ **Yes** |

## 🎯 Complete RAG Workflow

### Step 1: Scrape Content
```bash
python3 scrape_with_content.py
```

### Step 2: Load into Vector DB
```python
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import MarkdownTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

# Load markdown files
loader = DirectoryLoader('output/datadog_markdown_full/', glob='**/*.md')
documents = loader.load()

# Split into chunks (following RAG_GUIDE.md)
text_splitter = MarkdownTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_documents(documents)

# Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(chunks, embeddings)
```

### Step 3: Query
```python
# Semantic search
results = vectorstore.similarity_search(
    "How do I configure Datadog API?",
    k=3
)

for doc in results:
    print(doc.metadata['source'])
    print(doc.page_content)
```

## 📚 Documentation

| File | Purpose |
|------|---------|
| `CONTENT_SCRAPING_GUIDE.md` | **Start here!** Complete usage guide |
| `RAG_GUIDE.md` | RAG format specifications |
| `RAG_QUICKSTART.md` | Quick commands reference |
| `scrape_with_content.py` | Main content scraper |
| `run_content_scraper.sh` | Quick start script |

## ⚙️ Configuration

```bash
# Max depth (how deep to follow links)
export MAX_DEPTH=2

# Delay between requests (be respectful!)
export DELAY=1.0

# Then run
python3 scrape_with_content.py
```

### Depth Guide

| Depth | Pages | Time | Best For |
|-------|-------|------|----------|
| 1 | ~10-20 | 1-2 min | Testing |
| 2 | ~50-100 | 5-10 min | **Recommended** |
| 3 | ~200-500 | 15-30 min | Comprehensive |
| 4+ | ~1000+ | 1+ hour | Full docs |

## 🎁 Bonus: JSONL Export

Combine with the original scraper for multiple formats:

```bash
# 1. Get detailed markdown
python3 scrape_with_content.py

# 2. Also get JSONL for vector DBs
python3 main.py --api &
curl -X POST http://localhost:8000/scrape -d '{"max_depth": 2}'
curl http://localhost:8000/export/rag/jsonl -o datadog_rag.jsonl

# Now you have BOTH:
# ✅ Markdown files (human-readable, LangChain-ready)
# ✅ JSONL (vector DB ready, streaming-friendly)
```

## 🎉 You're All Set!

Run this command to start:

```bash
python3 scrape_with_content.py
```

Or for a guided experience:

```bash
./run_content_scraper.sh
```

The scraper will:
1. ✅ Recursively fetch all URLs up to specified depth
2. ✅ Extract full page content from each URL
3. ✅ Save to organized markdown files with metadata
4. ✅ Create an index and summary
5. ✅ Output RAG-ready format

Then use the markdown files with LangChain, ChromaDB, or any RAG framework!

**Happy scraping!** 🚀

---

*Files created: `scrape_with_content.py`, `run_content_scraper.sh`, `CONTENT_SCRAPING_GUIDE.md`*
