# RAG-Optimized File Formats for Datadog Scraper

## Overview
This guide explains how to save scraped Datadog documentation in formats optimized for Retrieval Augmented Generation (RAG) systems.

## Recommended RAG Formats

### 1. **JSONL (JSON Lines)** - Best for Vector Databases
Each line is a complete JSON document representing a page/chunk:

```jsonl
{"id": "doc_1", "url": "https://docs.datadoghq.com/api", "title": "API Documentation", "content": "...", "metadata": {"category": "api", "depth": 1, "timestamp": "2025-10-05"}}
{"id": "doc_2", "url": "https://docs.datadoghq.com/integrations", "title": "Integrations", "content": "...", "metadata": {"category": "integrations", "depth": 1, "timestamp": "2025-10-05"}}
```

**Use Cases:**
- Direct ingestion into Pinecone, Weaviate, Qdrant, ChromaDB
- Streaming processing for large datasets
- Easy to append and update individual records

### 2. **Markdown** - Best for LangChain/LlamaIndex
Structured markdown with metadata headers:

```markdown
---
url: https://docs.datadoghq.com/api
category: api
depth: 1
title: API Documentation
timestamp: 2025-10-05T10:30:00
---

# API Documentation

[Page content here...]
```

**Use Cases:**
- LangChain Document loaders
- LlamaIndex SimpleDirectoryReader
- Human-readable format for review
- Easy chunking with semantic splitters

### 3. **Parquet** - Best for Analytics & Large Scale RAG
Columnar storage format optimized for analytics:

```python
# Schema
- id: string
- url: string
- title: string
- content: string
- category: string
- depth: int
- parent_url: string
- scraped_at: timestamp
- embeddings: array<float>  # Optional: pre-computed vectors
```

**Use Cases:**
- Large-scale RAG pipelines
- Data analysis and filtering
- Efficient storage and querying
- Integration with Arrow/Polars/DuckDB

### 4. **Enhanced JSON** - Best for Metadata-Rich RAG
Comprehensive JSON with chunking and relationships:

```json
{
  "documents": [
    {
      "id": "doc_1",
      "url": "https://docs.datadoghq.com/api",
      "title": "API Documentation",
      "content": "Full page content...",
      "chunks": [
        {
          "chunk_id": "doc_1_chunk_0",
          "content": "First 512 tokens...",
          "start_char": 0,
          "end_char": 512
        }
      ],
      "metadata": {
        "category": "api",
        "depth": 1,
        "parent_url": "https://docs.datadoghq.com",
        "child_urls": ["https://docs.datadoghq.com/api/v1"],
        "tags": ["api", "rest", "http"],
        "scraped_at": "2025-10-05T10:30:00",
        "language": "en"
      },
      "outbound_links": 15,
      "inbound_links": 3
    }
  ],
  "metadata": {
    "total_documents": 150,
    "base_url": "https://docs.datadoghq.com",
    "scraping_date": "2025-10-05",
    "version": "1.0"
  }
}
```

## Implementation in Datadog Scraper

### Adding RAG Export Methods

Add these methods to `DatadogDocsScraper` class:

```python
def save_for_rag_jsonl(self, filename='datadog_rag.jsonl'):
    """Save in JSONL format for vector databases"""
    with open(filename, 'w', encoding='utf-8') as f:
        for i, url in enumerate(sorted(self.visited), 1):
            doc = {
                'id': f'doc_{i}',
                'url': url,
                'title': self._extract_title_from_url(url),
                'content': '',  # Fetch actual content if needed
                'metadata': {
                    'category': self._categorize_url(url),
                    'depth': self._get_depth(url),
                    'timestamp': datetime.now().isoformat()
                }
            }
            f.write(json.dumps(doc) + '\n')

def save_for_rag_markdown(self, output_dir='datadog_markdown'):
    """Save as individual markdown files"""
    os.makedirs(output_dir, exist_ok=True)
    
    for i, url in enumerate(sorted(self.visited), 1):
        category = self._categorize_url(url)
        safe_filename = self._url_to_filename(url)
        
        content = f"""---
url: {url}
category: {category}
depth: {self._get_depth(url)}
title: {self._extract_title_from_url(url)}
timestamp: {datetime.now().isoformat()}
---

# {self._extract_title_from_url(url)}

URL: {url}

[Content would be fetched here]
"""
        
        filepath = os.path.join(output_dir, f"{safe_filename}.md")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
```

### API Endpoint for RAG Export

Add to FastAPI app:

```python
@app.get("/export/rag/{format_type}")
async def export_for_rag(format_type: str):
    """Export scraping results in RAG-optimized formats"""
    
    if format_type == "jsonl":
        scraper.save_for_rag_jsonl()
        return FileResponse('datadog_rag.jsonl', 
                          media_type='application/x-ndjson',
                          filename='datadog_rag.jsonl')
    
    elif format_type == "markdown":
        scraper.save_for_rag_markdown()
        # Zip the directory
        import shutil
        shutil.make_archive('datadog_markdown', 'zip', 'datadog_markdown')
        return FileResponse('datadog_markdown.zip',
                          media_type='application/zip',
                          filename='datadog_markdown.zip')
```

## Vector Database Integration Examples

### Pinecone
```python
from pinecone import Pinecone
import json

pc = Pinecone(api_key="YOUR_KEY")
index = pc.Index("datadog-docs")

with open('datadog_rag.jsonl', 'r') as f:
    for line in f:
        doc = json.loads(line)
        # Generate embedding (use OpenAI, Cohere, etc.)
        embedding = generate_embedding(doc['content'])
        
        index.upsert([(
            doc['id'],
            embedding,
            doc['metadata']
        )])
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

# Load markdown files
loader = DirectoryLoader('datadog_markdown/', glob="**/*.md")
documents = loader.load()

# Split documents
text_splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(documents)

# Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(chunks, embeddings)
```

## Best Practices for RAG

### 1. **Content Extraction**
Currently, the scraper only collects URLs. For effective RAG, you need to:
- Extract actual page content (text, code examples)
- Remove navigation, headers, footers
- Preserve code blocks and formatting
- Extract headings for better chunking

```python
def extract_content(self, url):
    """Extract clean content from page"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Remove unwanted elements
    for element in soup(['nav', 'header', 'footer', 'script', 'style']):
        element.decompose()
    
    # Get main content
    main_content = soup.find('main') or soup.find('article') or soup.body
    
    return {
        'text': main_content.get_text(separator='\n', strip=True),
        'html': str(main_content),
        'title': soup.find('h1').get_text(strip=True) if soup.find('h1') else '',
        'headings': [h.get_text(strip=True) for h in main_content.find_all(['h1', 'h2', 'h3'])]
    }
```

### 2. **Chunking Strategy**
- **Size**: 512-1024 tokens per chunk
- **Overlap**: 100-200 tokens between chunks
- **Semantic**: Split on headers/sections when possible

### 3. **Metadata to Include**
- `url`: Original source
- `title`: Page title
- `category`: Content category
- `depth`: Scraping depth
- `timestamp`: When scraped
- `parent_url`: Hierarchical context
- `section`: Which part of page (for multi-chunk docs)

### 4. **Update Strategy**
- Use document IDs based on URL hash
- Track last_updated timestamps
- Implement incremental updates
- Version control for content changes

## Environment Variables

Add to `.env`:
```bash
# RAG Export Configuration
RAG_FORMAT=jsonl              # jsonl, markdown, parquet, json
RAG_CHUNK_SIZE=1000          # Token size per chunk
RAG_CHUNK_OVERLAP=200        # Token overlap between chunks
RAG_INCLUDE_CONTENT=true     # Extract full page content
RAG_EXTRACT_CODE=true        # Extract code blocks separately
RAG_METADATA_LEVEL=full      # minimal, standard, full
```

## Example Workflow

```bash
# 1. Scrape with content extraction
./start.sh --api --port 8000

# 2. Export for RAG
curl http://localhost:8000/export/rag/jsonl -o datadog_rag.jsonl

# 3. Load into vector database
python scripts/load_to_vectordb.py --input datadog_rag.jsonl --db pinecone

# 4. Query with RAG
python scripts/rag_query.py "How do I configure API keys in Datadog?"
```

## Comparison Matrix

| Format | Vector DB | Size | Human Readable | Streaming | Chunking |
|--------|-----------|------|----------------|-----------|----------|
| JSONL | ⭐⭐⭐⭐⭐ | Medium | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Manual |
| Markdown | ⭐⭐⭐ | Large | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Auto |
| Parquet | ⭐⭐⭐⭐ | Small | ⭐ | ⭐⭐⭐⭐ | Manual |
| JSON | ⭐⭐⭐ | Large | ⭐⭐⭐⭐ | ⭐⭐ | Flexible |

## Recommended Approach

**For most RAG use cases:**
1. Use **JSONL** as primary format (easy ingestion, streaming)
2. Use **Markdown** as backup (human review, debugging)
3. Store in **Parquet** for long-term archive and analytics

**File structure:**
```
output/
├── datadog_rag.jsonl           # Primary RAG format
├── datadog_markdown/           # Markdown files per page
│   ├── api-overview.md
│   ├── integrations-aws.md
│   └── ...
└── datadog_archive.parquet     # Long-term storage
```
