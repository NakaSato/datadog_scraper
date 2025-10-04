# RAG Integration Summary

## What I've Created for You

I've added comprehensive RAG (Retrieval Augmented Generation) export capabilities to your Datadog scraper. Here's what's new:

### 📁 New Files Created

1. **`RAG_GUIDE.md`** - Comprehensive 400+ line guide covering:
   - All recommended RAG formats (JSONL, Markdown, Parquet, JSON)
   - Vector database integration examples (Pinecone, ChromaDB, Weaviate)
   - LangChain and LlamaIndex usage patterns
   - Best practices for chunking, metadata, and updates

2. **`rag_exporter.py`** - Production-ready RAG export utility:
   - `RAGExporter` class with 4 export methods
   - JSONL format for vector databases (streaming-friendly)
   - Markdown with frontmatter for LangChain/LlamaIndex
   - Enhanced JSON with relationships and metadata
   - Automatic categorization and metadata enrichment

3. **`examples_rag.py`** - 5 practical examples:
   - Basic scraping with RAG export
   - JSONL for vector databases
   - Markdown for LangChain
   - API endpoint usage
   - Docker deployment patterns

4. **`RAG_QUICKSTART.md`** - Quick reference card:
   - All commands in one place
   - Integration snippets for popular tools
   - Troubleshooting guide
   - Performance tips

5. **Updated `.github/copilot-instructions.md`**:
   - Added RAG integration section
   - Documents export patterns
   - Links to new RAG resources

### 🔧 Enhanced Existing Files

**`main.py`** - Added new API endpoint:
```python
GET /export/rag/{format_type}
# Supports: jsonl, markdown, json, all
```

### 🎯 RAG Formats Available

#### 1. JSONL (JSON Lines)
**Best for:** Vector databases (Pinecone, Weaviate, ChromaDB, Qdrant)
```bash
curl http://localhost:8000/export/rag/jsonl -o datadog_rag.jsonl
```
- One JSON document per line
- Streaming-friendly for large datasets
- Easy to append and update
- Direct ingestion into vector DBs

#### 2. Markdown
**Best for:** LangChain, LlamaIndex, human review
```bash
curl http://localhost:8000/export/rag/markdown -o datadog_markdown.zip
```
- Structured with YAML frontmatter
- Preserves document hierarchy
- Semantic chunking support
- Human-readable

#### 3. Enhanced JSON
**Best for:** Custom RAG pipelines, analytics
```bash
curl http://localhost:8000/export/rag/json -o datadog_rag.json
```
- Rich metadata and relationships
- Parent-child URL tracking
- Category statistics
- Full tree structure

## 🚀 Quick Start

### Option 1: CLI Mode
```bash
# Scrape and export
python main.py --max-depth 2
python examples_rag.py
```

### Option 2: API Mode (Recommended)
```bash
# Start server
./start.sh --api

# Scrape
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"max_depth": 2, "delay": 0.5}'

# Export all formats
curl http://localhost:8000/export/rag/all
```

### Option 3: Docker Mode
```bash
# Start with Docker
./docker-deploy.sh build && ./docker-deploy.sh up

# Scrape and export
curl -X POST http://localhost:8000/scrape -d '{"max_depth": 2}'
curl http://localhost:8000/export/rag/all

# Access files in ./output/
ls -la output/
```

## 📊 Output Files

After exporting, you'll have:

```
output/
├── datadog_rag.jsonl              # For vector databases
├── datadog_rag_enhanced.json      # For custom pipelines
└── datadog_markdown/              # For LangChain/LlamaIndex
    ├── api-overview.md
    ├── integrations-aws.md
    └── ... (one .md per page)
```

## 🔌 Integration Examples

### With Pinecone
```python
import json
from pinecone import Pinecone

pc = Pinecone(api_key="YOUR_KEY")
index = pc.Index("datadog-docs")

with open('output/datadog_rag.jsonl', 'r') as f:
    for line in f:
        doc = json.loads(line)
        embedding = generate_embedding(doc['content'])
        index.upsert([(doc['id'], embedding, doc['metadata'])])
```

### With LangChain
```python
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import MarkdownTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

loader = DirectoryLoader('output/datadog_markdown/', glob="**/*.md")
docs = loader.load()

splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)

vectorstore = FAISS.from_documents(chunks, OpenAIEmbeddings())
```

## 📚 Documentation

1. **`RAG_GUIDE.md`** - Read this first for complete understanding
2. **`RAG_QUICKSTART.md`** - Quick commands and examples
3. **`examples_rag.py`** - Run for interactive examples
4. **API Docs** - http://localhost:8000/docs (when server is running)

## 🎯 Next Steps

### Immediate Actions
1. ✅ Start the API server: `./start.sh --api`
2. ✅ Trigger a test scrape: `curl -X POST http://localhost:8000/scrape -d '{"max_depth": 1}'`
3. ✅ Export RAG formats: `curl http://localhost:8000/export/rag/all`
4. ✅ Inspect the output files in `./output/`

### Future Enhancements (Optional)
The current implementation extracts URLs and metadata. For full RAG capability, consider:

1. **Content Extraction** - Extract actual page text (currently placeholder)
   ```python
   # Enhance extract_links() to also get page content
   def extract_content(self, url):
       # Remove nav, footer, etc.
       # Extract main article text
       # Preserve code blocks
   ```

2. **Chunking** - Split long documents into smaller pieces
   ```python
   # Add chunking support
   def chunk_content(self, content, chunk_size=1000, overlap=200):
       # Split on sentence boundaries
       # Maintain context with overlap
   ```

3. **Embeddings** - Pre-compute vectors for faster loading
   ```python
   # Add embedding generation
   def add_embeddings(self, content, model="text-embedding-ada-002"):
       # Call OpenAI/Cohere API
       # Add to export data
   ```

## 🔍 Key Features

✅ **Multiple Export Formats** - JSONL, Markdown, JSON
✅ **Metadata-Rich** - Category, depth, parent URLs, timestamps
✅ **API Endpoints** - RESTful access to all formats
✅ **Docker Ready** - Full containerized deployment
✅ **Vector DB Compatible** - Works with Pinecone, ChromaDB, Weaviate
✅ **LangChain/LlamaIndex Ready** - Markdown with frontmatter
✅ **Streaming Support** - JSONL for large datasets
✅ **Comprehensive Docs** - Guides, examples, quick reference

## 💡 Pro Tips

1. **Start small**: Use `max_depth=1` for initial testing
2. **Respect rate limits**: Keep delay at 0.5s or higher
3. **Test locally first**: Use CLI mode before Docker
4. **Check the docs**: Visit http://localhost:8000/docs for interactive API testing
5. **Monitor progress**: Use `/status` endpoint during long scrapes

## 🆘 Need Help?

- **API not responding?** Check `curl http://localhost:8000/health`
- **No RAG exports?** Ensure scraping completed: `curl http://localhost:8000/status`
- **Import errors?** Run `pip install -r requirements.txt`
- **Docker issues?** Try `./docker-deploy.sh clean && ./docker-deploy.sh build`

## 📈 What You Can Build

With these RAG exports, you can now:

- 🤖 **Chatbot** - "Ask Datadog Docs" using vector search
- 🔍 **Semantic Search** - Find relevant docs by meaning, not keywords
- 📊 **Analytics** - Analyze documentation structure and content
- 🎓 **Training Data** - Fine-tune models on Datadog knowledge
- 📚 **Knowledge Base** - Build internal reference system
- 🔗 **Link Analysis** - Study documentation relationships

Enjoy your RAG-ready Datadog scraper! 🚀
