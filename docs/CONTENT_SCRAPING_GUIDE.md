# How to Run Deep Path Content Scraping

## 🎯 Goal
Fetch all paths from Datadog documentation with deep scraping, extract full content, and save to markdown files following RAG_GUIDE.md specifications.

## 📋 Prerequisites

```bash
# Install dependencies
pip install requests beautifulsoup4 fastapi uvicorn

# Or if using the existing requirements
pip install -r requirements.txt
```

## 🚀 Quick Start

### Option 1: Using the Enhanced Scraper (Recommended)

```bash
# Basic usage (depth=1, delay=0.5s)
python3 scrape_with_content.py

# Custom depth and delay
MAX_DEPTH=2 DELAY=1.0 python3 scrape_with_content.py

# Deep scraping (WARNING: Takes much longer!)
MAX_DEPTH=3 DELAY=1.5 python3 scrape_with_content.py
```

### Option 2: Using the Quick Start Script

```bash
# Make executable
chmod +x run_content_scraper.sh

# Run with defaults (depth=2, delay=1.0s)
./run_content_scraper.sh

# Run with custom settings
./run_content_scraper.sh 3 1.5
# (depth=3, delay=1.5s)
```

## 📊 What Gets Scraped

The enhanced scraper extracts:

✅ **Full page content** (not just URLs)
✅ **Page titles** and headings
✅ **Code blocks** with language detection  
✅ **Document structure** (h1-h6 hierarchy)
✅ **Metadata** (category, depth, parent URL, timestamps)
✅ **Clean text** (removes nav, footer, scripts)

## 📁 Output Structure

```
output/datadog_markdown_full/
├── INDEX.md                    # Complete index of all docs
├── SUMMARY.json               # Statistics and metadata
├── api/                       # Category: API docs
│   ├── api-overview.md
│   ├── api-v1-endpoints.md
│   └── ...
├── integrations/              # Category: Integrations
│   ├── integrations-aws.md
│   ├── integrations-azure.md
│   └── ...
└── getting-started/           # Category: Getting Started
    └── ...
```

## 📄 Markdown File Format

Each file follows RAG_GUIDE.md specifications:

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
**Category:** api | **Depth:** 1

---

## Table of Contents

- API Overview
  - Authentication
  - Rate Limiting
- API Endpoints
  - Metrics
  - Events

---

## Content

[Full extracted content here...]

## Code Examples

### Example 1 (python)

```python
import requests
...
```

---

*Extracted: 2025-10-05T10:30:00*
*Word Count: 1524*
```

## ⚙️ Configuration

### Environment Variables

```bash
# Maximum depth to follow links
export MAX_DEPTH=2

# Delay between requests (be respectful!)
export DELAY=1.0

# Then run
python3 scrape_with_content.py
```

### Depth Recommendations

| Depth | Pages | Time | Use Case |
|-------|-------|------|----------|
| 1 | ~10-20 | 1-2 min | Testing, main sections |
| 2 | ~50-100 | 5-10 min | Good coverage |
| 3 | ~200-500 | 15-30 min | Comprehensive |
| 4+ | ~1000+ | 1+ hour | Full documentation |

**⚠️ Start with depth=1 for testing!**

## 📊 After Scraping

### View the Results

```bash
# Open the index
cat output/datadog_markdown_full/INDEX.md

# Check summary statistics
cat output/datadog_markdown_full/SUMMARY.json

# View a sample file
cat output/datadog_markdown_full/api/api-overview.md

# Count total files
find output/datadog_markdown_full -name "*.md" -not -name "INDEX.md" | wc -l
```

### Use with LangChain

```python
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import MarkdownTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

# Load all markdown files
loader = DirectoryLoader(
    'output/datadog_markdown_full/',
    glob='**/*.md',
    exclude=['INDEX.md']
)
documents = loader.load()

print(f"Loaded {len(documents)} documents")

# Split into chunks
text_splitter = MarkdownTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks")

# Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(chunks, embeddings)

# Query
query = "How do I configure API keys in Datadog?"
docs = vectorstore.similarity_search(query, k=3)

for doc in docs:
    print(f"\n{doc.metadata['source']}")
    print(doc.page_content[:200])
```

### Use with ChromaDB

```python
import chromadb
from pathlib import Path

client = chromadb.Client()
collection = client.create_collection("datadog-docs")

# Load markdown files
md_dir = Path('output/datadog_markdown_full')
for md_file in md_dir.rglob('*.md'):
    if md_file.name == 'INDEX.md':
        continue
    
    content = md_file.read_text()
    
    # Extract metadata from frontmatter
    # (parse YAML frontmatter here)
    
    collection.add(
        documents=[content],
        metadatas=[{'source': str(md_file)}],
        ids=[str(md_file)]
    )

# Query
results = collection.query(
    query_texts=["How to use Datadog API"],
    n_results=3
)
```

## 🔄 Combining with JSONL Export

For complete RAG setup, combine both approaches:

```bash
# 1. Extract content to markdown (detailed, human-readable)
python3 scrape_with_content.py

# 2. Also export to JSONL (for vector DBs)
python3 main.py --api &
sleep 5
curl -X POST http://localhost:8000/scrape -d '{"max_depth": 2}'
# Wait for completion
curl http://localhost:8000/export/rag/jsonl -o datadog_rag.jsonl

# Now you have:
# - output/datadog_markdown_full/ (for LangChain)
# - datadog_rag.jsonl (for Pinecone/ChromaDB)
```

## 🎯 Example Workflows

### Workflow 1: Build a Documentation Chatbot

```bash
# 1. Scrape content
MAX_DEPTH=2 python3 scrape_with_content.py

# 2. Load into vector DB (Python)
python3 << 'EOF'
from langchain.document_loaders import DirectoryLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

loader = DirectoryLoader('output/datadog_markdown_full/', glob='**/*.md')
docs = loader.load()

vectorstore = Chroma.from_documents(
    docs,
    OpenAIEmbeddings(),
    persist_directory='./chroma_db'
)
print(f"Loaded {len(docs)} documents into Chroma")
EOF

# 3. Query (Python)
python3 << 'EOF'
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

vectorstore = Chroma(
    persist_directory='./chroma_db',
    embedding_function=OpenAIEmbeddings()
)

results = vectorstore.similarity_search(
    "How do I set up Datadog monitoring?",
    k=3
)

for doc in results:
    print(f"\n{'='*60}")
    print(doc.page_content[:300])
EOF
```

### Workflow 2: Create Documentation Search

```bash
# 1. Scrape with deep paths
MAX_DEPTH=3 DELAY=1.5 python3 scrape_with_content.py

# 2. Use the markdown files directly
find output/datadog_markdown_full -name "*.md" -exec grep -l "monitoring" {} \;

# 3. Or build a search index
python3 << 'EOF'
import json
from pathlib import Path

index = {}
md_dir = Path('output/datadog_markdown_full')

for md_file in md_dir.rglob('*.md'):
    content = md_file.read_text()
    # Simple keyword indexing
    for word in ['api', 'integration', 'monitoring', 'metrics']:
        if word in content.lower():
            if word not in index:
                index[word] = []
            index[word].append(str(md_file))

# Save index
with open('search_index.json', 'w') as f:
    json.dump(index, f, indent=2)

print("Search index created!")
EOF
```

## 🐛 Troubleshooting

### ModuleNotFoundError: No module named 'requests'
```bash
pip install requests beautifulsoup4
```

### Permission denied
```bash
chmod +x scrape_with_content.py
chmod +x run_content_scraper.sh
```

### Too slow / timeout errors
```bash
# Reduce depth
MAX_DEPTH=1 python3 scrape_with_content.py

# Increase delay between requests
DELAY=2.0 python3 scrape_with_content.py
```

### Rate limiting from Datadog
```bash
# Increase delay significantly
DELAY=3.0 python3 scrape_with_content.py

# Or scrape in smaller batches (lower depth)
```

## 📚 Related Documentation

- **RAG_GUIDE.md** - Complete RAG integration guide
- **RAG_QUICKSTART.md** - Quick commands reference
- **examples_rag.py** - Code examples for RAG usage
- **rag_exporter.py** - JSONL/JSON export utilities

## ✨ Summary

You now have a complete solution that:

1. ✅ Fetches all paths from URLs with configurable depth
2. ✅ Extracts full page content (not just URLs)  
3. ✅ Saves to markdown files following RAG_GUIDE.md format
4. ✅ Organizes by category automatically
5. ✅ Includes metadata, headings, code blocks
6. ✅ Creates index and summary files
7. ✅ Ready for LangChain, ChromaDB, Pinecone, etc.

**Start scraping:**
```bash
python3 scrape_with_content.py
```

Happy scraping! 🚀
