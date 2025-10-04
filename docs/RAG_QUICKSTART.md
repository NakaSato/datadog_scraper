# RAG Export Quick Reference

## 🎯 Quick Commands

### CLI Usage
```bash
# 1. Scrape with RAG export
python main.py --max-depth 2
python -c "from main import scraper; from rag_exporter import RAGExporter; exporter = RAGExporter(scraper); exporter.export_all()"

# 2. Use example script
python examples_rag.py
```

### API Usage
```bash
# Start API server
./start.sh --api --port 8000

# Scrape
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"max_depth": 2, "delay": 0.5}'

# Export JSONL (for vector databases)
curl http://localhost:8000/export/rag/jsonl -o datadog_rag.jsonl

# Export Markdown (for LangChain)
curl http://localhost:8000/export/rag/markdown -o datadog_markdown.zip

# Export all formats
curl http://localhost:8000/export/rag/all
```

### Docker Usage
```bash
# Start with Docker
./docker-deploy.sh build && ./docker-deploy.sh up

# Scrape via API
curl -X POST http://localhost:8000/scrape -d '{"max_depth": 2}'

# Export RAG formats
curl http://localhost:8000/export/rag/all

# Access files (mounted at ./output/)
ls -la output/
```

## 📊 Output Formats

### JSONL (`datadog_rag.jsonl`)
**Best for:** Pinecone, Weaviate, ChromaDB, Qdrant
```jsonl
{"id": "datadog_doc_1", "url": "...", "title": "...", "content": "...", "metadata": {...}}
{"id": "datadog_doc_2", "url": "...", "title": "...", "content": "...", "metadata": {...}}
```

### Markdown (`datadog_markdown/*.md`)
**Best for:** LangChain, LlamaIndex
```markdown
---
url: https://docs.datadoghq.com/api
category: api
depth: 1
---
# API Documentation
...
```

### Enhanced JSON (`datadog_rag_enhanced.json`)
**Best for:** Custom RAG pipelines, analytics
```json
{
  "documents": [...],
  "metadata": {
    "total_documents": 150,
    "categories": {...}
  }
}
```

## 🔌 Vector Database Integration

### Pinecone
```python
from pinecone import Pinecone
import json

pc = Pinecone(api_key="YOUR_KEY")
index = pc.Index("datadog-docs")

with open('datadog_rag.jsonl', 'r') as f:
    for line in f:
        doc = json.loads(line)
        embedding = generate_embedding(doc['content'])
        index.upsert([(doc['id'], embedding, doc['metadata'])])
```

### ChromaDB
```python
import chromadb
import json

client = chromadb.Client()
collection = client.create_collection("datadog-docs")

with open('datadog_rag.jsonl', 'r') as f:
    for line in f:
        doc = json.loads(line)
        collection.add(
            documents=[doc['content']],
            metadatas=[doc['metadata']],
            ids=[doc['id']]
        )
```

### LangChain
```python
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import MarkdownTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

loader = DirectoryLoader('datadog_markdown/', glob="**/*.md")
documents = loader.load()

text_splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(chunks, embeddings)
```

## 🚀 Full Workflow Example

```bash
# 1. Start API
./start.sh --api

# 2. Trigger scraping
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"max_depth": 2, "delay": 0.5}'

# 3. Wait for completion (check status)
while true; do
  STATUS=$(curl -s http://localhost:8000/status | jq -r '.is_scraping')
  if [ "$STATUS" = "false" ]; then break; fi
  echo "Still scraping..."
  sleep 5
done

# 4. Export all RAG formats
curl http://localhost:8000/export/rag/all

# 5. Files are now in ./output/
ls -la output/
# - datadog_rag.jsonl
# - datadog_markdown/
# - datadog_rag_enhanced.json

# 6. Load into vector database
python load_to_vectordb.py --input output/datadog_rag.jsonl
```

## 📁 File Structure

```
output/
├── datadog_rag.jsonl              # JSONL for vector DBs
├── datadog_rag_enhanced.json      # Enhanced JSON with metadata
├── datadog_markdown/              # Markdown files
│   ├── api-overview.md
│   ├── integrations-aws.md
│   └── ...
├── datadog_all_links.txt          # Simple URL list
├── datadog_links_detailed.txt     # Categorized URLs
└── datadog_links.json             # Original JSON format
```

## 🎛️ Configuration

### Environment Variables
```bash
# RAG Export Settings
RAG_FORMAT=jsonl              # Default format
RAG_CHUNK_SIZE=1000          # Tokens per chunk
RAG_CHUNK_OVERLAP=200        # Overlap between chunks
RAG_INCLUDE_CONTENT=true     # Extract full content
```

### API Request Parameters
```json
{
  "max_depth": 2,
  "delay": 0.5,
  "save_results": true
}
```

## 📚 Learn More

- **RAG_GUIDE.md** - Comprehensive RAG integration guide
- **examples_rag.py** - Python examples for all formats
- **.github/copilot-instructions.md** - Architecture and patterns
- **API Docs** - http://localhost:8000/docs (when running)

## 🔍 Common Use Cases

| Use Case | Format | Tool |
|----------|--------|------|
| Semantic search | JSONL | Pinecone, Weaviate |
| Document Q&A | Markdown | LangChain, LlamaIndex |
| Analytics | Enhanced JSON | Custom pipeline |
| Chat with docs | JSONL | ChromaDB + OpenAI |
| Knowledge base | Markdown | RAG framework |

## ⚡ Performance Tips

1. **Start with shallow depth** (max_depth=1) for testing
2. **Use appropriate delay** (0.5-1.0s) to respect servers
3. **Export incrementally** for large datasets
4. **Chunk documents** before embedding (512-1024 tokens)
5. **Include metadata** for better filtering and context

## 🆘 Troubleshooting

```bash
# RAG exporter not found
pip install -r requirements.txt

# No results available
# Make sure to run scraping first:
curl -X POST http://localhost:8000/scrape -d '{"max_depth": 2}'

# Check scraping status
curl http://localhost:8000/status

# View logs
./docker-deploy.sh logs -f

# Test export manually
python -c "from main import scraper; from rag_exporter import RAGExporter; print(RAGExporter(scraper))"
```
