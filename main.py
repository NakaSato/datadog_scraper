#!/usr/bin/env python3
"""
Datadog Documentation Scraper - Unified Multi-Mode Tool

This script provides comprehensive web scraping capabilities for Datadog documentation
with multiple operational modes and RAG-optimized export formats.

Usage Modes:
    1. CLI Scraping (default):
       python main.py --max-depth 3 --delay 1.0
       
    2. Content Extraction (full page content):
       python main.py --extract-content --max-depth 2
       
    3. RAG Export:
       python main.py --export-rag all
       python main.py --export-rag jsonl --output-dir ./rag_output
       
    4. API Server:
       python main.py --api --port 8000
       
    5. Combined:
       python main.py --max-depth 3 --extract-content --export-rag all

Features:
    - Recursive link discovery and tree structure mapping
    - Full HTML content extraction with metadata
    - RAG-optimized exports (JSONL, Markdown, JSON)
    - REST API with FastAPI for webhook integration
    - Docker-ready with environment variable support
    - n8n integration via webhook endpoints
"""

import sys
import os
import re
import json
import time
import requests
import threading
import argparse
from collections import defaultdict
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import Optional, Set, List, Dict

# FastAPI imports (only used in API mode)
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn


# ============================================================================
# Content Extraction Classes
# ============================================================================

class ContentExtractor:
    """Extract clean content from web pages for RAG"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def extract_content(self, url: str) -> Dict:
        """Extract clean content from a page"""
        response = requests.get(url, headers=self.headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['nav', 'header', 'footer', 'script', 'style', 'iframe']):
            element.decompose()
        
        # Find main content
        main_content = (
            soup.find('main') or 
            soup.find('article') or 
            soup.find('div', {'class': re.compile(r'content|main|article', re.I)}) or
            soup.body
        )
        
        if not main_content:
            return self._empty_content(url)
        
        # Extract components
        title = self._extract_title(soup, main_content)
        headings = self._extract_headings(main_content)
        text = main_content.get_text(separator='\n', strip=True)
        code_blocks = self._extract_code_blocks(main_content)
        text = self._clean_text(text)
        
        return {
            'url': url,
            'title': title,
            'text': text,
            'headings': headings,
            'code_blocks': code_blocks,
            'word_count': len(text.split()),
            'extracted_at': datetime.now().isoformat()
        }
    
    def _extract_title(self, soup, content) -> str:
        title = soup.find('h1') or soup.find('title') or content.find('h1')
        return title.get_text(strip=True) if title else "Untitled"
    
    def _extract_headings(self, content) -> List[Dict]:
        headings = []
        for tag in content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append({
                'level': int(tag.name[1]),
                'text': tag.get_text(strip=True),
                'id': tag.get('id', '')
            })
        return headings
    
    def _extract_code_blocks(self, content) -> List[Dict]:
        code_blocks = []
        for pre in content.find_all('pre'):
            code = pre.find('code')
            if code:
                classes = code.get('class', [])
                language = 'text'
                for cls in classes:
                    if isinstance(cls, str) and cls.startswith('language-'):
                        language = cls.replace('language-', '')
                        break
                code_blocks.append({
                    'language': language,
                    'code': code.get_text(strip=False)
                })
        return code_blocks
    
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        return text.strip()
    
    def _empty_content(self, url: str) -> Dict:
        return {
            'url': url,
            'title': 'Untitled',
            'text': '',
            'headings': [],
            'code_blocks': [],
            'word_count': 0,
            'extracted_at': datetime.now().isoformat()
        }


class RAGExporter:
    """Export scraped data in RAG-optimized formats"""
    
    def __init__(self, scraper):
        self.scraper = scraper
        
    def _categorize_url(self, url: str) -> str:
        path_parts = urlparse(url).path.strip('/').split('/')
        return path_parts[0] if path_parts and path_parts[0] else 'root'
    
    def _extract_title_from_url(self, url: str) -> str:
        path = urlparse(url).path.strip('/')
        if not path:
            return "Home"
        title = path.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
        return title or "Home"
    
    def _url_to_filename(self, url: str) -> str:
        path = urlparse(url).path.strip('/')
        filename = path.replace('/', '-').replace('_', '-')
        filename = re.sub(r'[^\w\-]', '', filename)
        return filename[:200] or 'index'
    
    def _get_depth(self, url: str) -> int:
        base_parts = urlparse(self.scraper.base_url).path.strip('/').split('/')
        url_parts = urlparse(url).path.strip('/').split('/')
        return len(url_parts) - len(base_parts)
    
    def _get_parent_url(self, url: str) -> Optional[str]:
        for parent, children in self.scraper.links_tree.items():
            for child in children:
                if child['url'] == url:
                    return parent
        return None
    
    def save_jsonl(self, filename: str = 'output/datadog_rag.jsonl') -> int:
        """Save in JSONL format for vector databases"""
        os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
        
        count = 0
        with open(filename, 'w', encoding='utf-8') as f:
            for i, url in enumerate(sorted(self.scraper.visited), 1):
                doc = {
                    'id': f'datadog_doc_{i}',
                    'url': url,
                    'title': self._extract_title_from_url(url),
                    'content': '',
                    'metadata': {
                        'category': self._categorize_url(url),
                        'depth': self._get_depth(url),
                        'parent_url': self._get_parent_url(url),
                        'scraped_at': datetime.now().isoformat(),
                        'source': 'datadog_docs',
                        'base_url': self.scraper.base_url
                    }
                }
                f.write(json.dumps(doc, ensure_ascii=False) + '\n')
                count += 1
        
        print(f"✅ Exported {count} documents to {filename} (JSONL format)")
        return count
    
    def save_markdown(self, output_dir: str = 'output/datadog_markdown') -> int:
        """Save as individual markdown files"""
        os.makedirs(output_dir, exist_ok=True)
        
        count = 0
        for url in sorted(self.scraper.visited):
            category = self._categorize_url(url)
            safe_filename = self._url_to_filename(url)
            parent_url = self._get_parent_url(url)
            
            # Create category subdirectory
            category_dir = os.path.join(output_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            
            # Build markdown with frontmatter
            frontmatter = f"""---
url: {url}
category: {category}
depth: {self._get_depth(url)}
title: {self._extract_title_from_url(url)}
parent_url: {parent_url or 'none'}
scraped_at: {datetime.now().isoformat()}
source: datadog_docs
---

"""
            
            content = f"""# {self._extract_title_from_url(url)}

**URL:** [{url}]({url})
**Category:** {category}

<!-- Content extraction requires full scraping with --extract-content flag -->

This document was scraped from Datadog documentation.

"""
            
            filepath = os.path.join(category_dir, f"{safe_filename}.md")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(frontmatter + content)
            
            count += 1
        
        print(f"✅ Exported {count} markdown files to {output_dir}/")
        return count
    
    def save_enhanced_json(self, filename: str = 'output/datadog_rag_enhanced.json') -> Dict:
        """Save enhanced JSON with rich metadata"""
        os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
        
        documents = []
        categories = {}
        
        for i, url in enumerate(sorted(self.scraper.visited), 1):
            category = self._categorize_url(url)
            parent = self._get_parent_url(url)
            children = [child['url'] for child in self.scraper.links_tree.get(url, [])]
            
            if category not in categories:
                categories[category] = []
            categories[category].append(url)
            
            doc = {
                'id': f'datadog_doc_{i}',
                'url': url,
                'title': self._extract_title_from_url(url),
                'content': '',
                'metadata': {
                    'category': category,
                    'depth': self._get_depth(url),
                    'parent_url': parent,
                    'child_urls': children,
                    'child_count': len(children),
                    'scraped_at': datetime.now().isoformat(),
                    'source': 'datadog_docs',
                    'language': 'en'
                }
            }
            documents.append(doc)
        
        output = {
            'documents': documents,
            'metadata': {
                'total_documents': len(documents),
                'base_url': self.scraper.base_url,
                'max_depth': self.scraper.max_depth,
                'scraping_date': datetime.now().isoformat(),
                'categories': {cat: len(urls) for cat, urls in categories.items()},
                'version': '1.0',
                'format': 'rag_enhanced'
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        stats = {
            'total_documents': len(documents),
            'categories': len(categories),
            'file': filename
        }
        
        print(f"✅ Exported enhanced JSON with {stats['total_documents']} documents")
        return stats
    
    def export_all(self, base_dir: str = 'output') -> Dict:
        """Export all RAG-optimized formats"""
        print("🚀 Exporting scraped data in RAG-optimized formats...\n")
        
        results = {
            'jsonl': self.save_jsonl(f'{base_dir}/datadog_rag.jsonl'),
            'markdown': self.save_markdown(f'{base_dir}/datadog_markdown'),
            'enhanced_json': self.save_enhanced_json(f'{base_dir}/datadog_rag_enhanced.json')
        }
        
        print(f"\n✨ Export complete! {results['jsonl']} documents in {len(results)} formats")
        return results


# ============================================================================
# Core Scraper Class
# ============================================================================


class DatadogDocsScraper:
    def __init__(self, base_url, max_depth=2, delay=0.5):
        self.base_url = base_url
        self.max_depth = max_depth
        self.delay = delay  # Delay between requests (be respectful)
        self.visited = set()
        self.links_tree = defaultdict(list)
        self.domain = urlparse(base_url).netloc
        self.is_scraping = False
        self.last_scraped = None
        self.results = {}

    def is_valid_url(self, url):
        """Check if URL belongs to the same domain"""
        parsed = urlparse(url)
        return parsed.netloc == self.domain

    def normalize_url(self, url):
        """Remove fragments and trailing slashes for consistency"""
        parsed = urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if normalized.endswith('/'):
            normalized = normalized[:-1]
        return normalized

    def extract_links(self, url):
        """Extract all links from a given URL"""
        print(f"Scraping: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        links = []

        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(url, href)

            # Only include links from same domain
            if self.is_valid_url(absolute_url):
                normalized = self.normalize_url(absolute_url)
                links.append({
                    'text': link.get_text(strip=True),
                    'url': normalized
                })

        return links

    def scrape_recursive(self, url, depth=0, parent_url=None):
        """Recursively scrape links up to max_depth"""
        normalized_url = self.normalize_url(url)

        # Stop conditions
        if depth > self.max_depth:
            return

        if normalized_url in self.visited:
            return

        self.visited.add(normalized_url)

        # Extract links from current page
        links = self.extract_links(url)

        # Store in tree structure
        if parent_url:
            parent_normalized = self.normalize_url(parent_url)
            self.links_tree[parent_normalized].append({
                'url': normalized_url,
                'depth': depth,
                'children': []
            })

        # Add delay to be respectful
        time.sleep(self.delay)

        # Recursively scrape child links
        for link in links:
            child_url = link['url']
            if child_url not in self.visited:
                self.scrape_recursive(child_url, depth + 1, normalized_url)

        return links

    def get_all_links(self):
        """Get all discovered links"""
        return sorted(list(self.visited))

    def save_results(self, filename='datadog_all_links.txt',
                     json_filename='datadog_links.json',
                     detailed_filename='datadog_links_detailed.txt'):
        """Save results to files"""

        # Save simple text file (just URLs)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Datadog Documentation Links\n")
            f.write(f"Scraped from: {self.base_url}\n")
            f.write(f"Total links found: {len(self.visited)}\n")
            f.write(f"Max depth: {self.max_depth}\n")
            f.write("="*80 + "\n\n")
            for url in sorted(self.visited):
                f.write(f"{url}\n")

        # Save detailed text file with categorization
        with open(detailed_filename, 'w', encoding='utf-8') as f:
            f.write(f"Datadog Documentation Links - Detailed Report\n")
            f.write(f"Scraped from: {self.base_url}\n")
            f.write(f"Total links found: {len(self.visited)}\n")
            f.write(f"Max depth: {self.max_depth}\n")
            f.write("="*80 + "\n\n")

            # Categorize links by section
            categorized = defaultdict(list)
            for url in sorted(self.visited):
                # Extract category from URL path
                path_parts = urlparse(url).path.strip('/').split('/')
                category = path_parts[0] if path_parts and path_parts[0] else 'root'
                categorized[category].append(url)

            # Write categorized links
            for category in sorted(categorized.keys()):
                f.write(f"\n{'='*80}\n")
                f.write(f"Category: {category.upper()}\n")
                f.write(f"Count: {len(categorized[category])}\n")
                f.write(f"{'='*80}\n\n")
                for i, url in enumerate(categorized[category], 1):
                    f.write(f"{i}. {url}\n")

        # Save as JSON with tree structure
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'total_links': len(self.visited),
                'base_url': self.base_url,
                'max_depth': self.max_depth,
                'links': sorted(list(self.visited)),
                'tree': dict(self.links_tree)
            }, f, indent=2)

        print(f"\nResults saved to:")
        print(f"  - {filename} (simple list)")
        print(f"  - {detailed_filename} (categorized)")
        print(f"  - {json_filename} (JSON format)")


# Global scraper instance
scraper = DatadogDocsScraper(base_url="https://docs.datadoghq.com/")

# FastAPI app instance
app = FastAPI(
    title="Datadog Scraper API",
    description="API for scraping Datadog documentation with n8n integration",
    version="1.0.0"
)

# Pydantic models for API
class ScrapeRequest(BaseModel):
    max_depth: Optional[int] = 2
    delay: Optional[float] = 0.5
    save_results: Optional[bool] = True

class ScrapeResponse(BaseModel):
    status: str
    message: str
    total_links: int
    scraping_time: float
    timestamp: str

class WebhookPayload(BaseModel):
    action: str
    data: Optional[Dict] = None


def run_scraping(max_depth: int = 2, delay: float = 0.5, save_results: bool = True):
    """Run the scraping process"""
    global scraper

    # Reset scraper state
    scraper = DatadogDocsScraper(
        base_url="https://docs.datadoghq.com/",
        max_depth=max_depth,
        delay=delay
    )

    scraper.is_scraping = True
    start_time = time.time()

    scraper.scrape_recursive(scraper.base_url)
    scraping_time = time.time() - start_time
    scraper.last_scraped = datetime.now().isoformat()

    # Store results
    scraper.results = {
        'total_links': len(scraper.visited),
        'base_url': scraper.base_url,
        'max_depth': scraper.max_depth,
        'links': scraper.get_all_links(),
        'tree': dict(scraper.links_tree),
        'scraping_time': scraping_time,
        'timestamp': scraper.last_scraped
    }

    if save_results:
        scraper.save_results()

    scraper.is_scraping = False
    return True


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Datadog Scraper API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "n8n_integration": True
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for n8n"""
    return {
        "status": "healthy",
        "is_scraping": scraper.is_scraping,
        "last_scraped": scraper.last_scraped
    }


@app.post("/scrape")
async def trigger_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """Trigger scraping process (for n8n webhooks)"""

    background_tasks.add_task(run_scraping, request.max_depth, request.delay, request.save_results)

    return {
        "status": "started",
        "message": "Scraping process initiated",
        "estimated_completion": "Check /status for progress"
    }


@app.get("/status")
async def get_status():
    """Get current scraping status"""
    return {
        "is_scraping": scraper.is_scraping,
        "last_scraped": scraper.last_scraped,
        "total_links": len(scraper.visited) if not scraper.is_scraping else 0,
        "results_available": scraper.results != {}
    }


@app.get("/results")
async def get_results():
    """Get scraping results"""

    return JSONResponse(content=scraper.results)


@app.get("/results/json")
async def download_json():
    """Download results as JSON file"""

    # Save current results to file
    json_filename = 'datadog_links_api.json'
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(scraper.results, f, indent=2)

    return FileResponse(
        json_filename,
        media_type='application/json',
        filename='datadog_scraper_results.json'
    )


@app.post("/webhook")
async def n8n_webhook(payload: WebhookPayload):
    """Webhook endpoint for n8n integration"""

    if payload.action == "start_scraping":
        # Trigger scraping with default parameters
        threading.Thread(target=run_scraping, daemon=True).start()

        return {
            "status": "success",
            "message": "Scraping started via webhook",
            "timestamp": datetime.now().isoformat()
        }

    elif payload.action == "get_results":
        return {
            "status": "success",
            "data": scraper.results,
            "timestamp": datetime.now().isoformat()
        }


@app.get("/export/rag/{format_type}")
async def export_rag(format_type: str):
    """
    Export scraping results in RAG-optimized formats
    
    Supported formats:
    - jsonl: JSON Lines format for vector databases (Pinecone, Weaviate, ChromaDB)
    - markdown: Markdown files with frontmatter for LangChain/LlamaIndex
    - json: Enhanced JSON with metadata and relationships
    - all: Export all formats
    """
    exporter = RAGExporter(scraper)
    
    if format_type == "jsonl":
        exporter.save_jsonl()
        return FileResponse(
            'output/datadog_rag.jsonl',
            media_type='application/x-ndjson',
            filename='datadog_rag.jsonl'
        )
    
    elif format_type == "markdown":
        exporter.save_markdown()
        # Create zip file
        import shutil
        shutil.make_archive('output/datadog_markdown', 'zip', 'output/datadog_markdown')
        return FileResponse(
            'output/datadog_markdown.zip',
            media_type='application/zip',
            filename='datadog_markdown.zip'
        )
    
    elif format_type == "json":
        stats = exporter.save_enhanced_json()
        return FileResponse(
            'output/datadog_rag_enhanced.json',
            media_type='application/json',
            filename='datadog_rag_enhanced.json'
        )
    
    elif format_type == "all":
        stats = exporter.export_all()
        return JSONResponse(content={
            "status": "success",
            "message": "All RAG formats exported",
            "statistics": stats,
            "files": {
                "jsonl": "output/datadog_rag.jsonl",
                "markdown": "output/datadog_markdown/",
                "json": "output/datadog_rag_enhanced.json"
            }
        })
def print_tree(scraper, url, visited_in_tree=None, prefix="", is_last=True):
    """Print links in a tree structure"""
    if visited_in_tree is None:
        visited_in_tree = set()

    if url in visited_in_tree:
        return

    visited_in_tree.add(url)

    # Print current URL
    connector = "└── " if is_last else "├── "
    print(f"{prefix}{connector}{url}")

    # Get children
    children = scraper.links_tree.get(url, [])

    # Print children
    for i, child in enumerate(children):
        child_url = child['url']
        is_last_child = (i == len(children) - 1)
        extension = "    " if is_last else "│   "
        print_tree(scraper, child_url, visited_in_tree, prefix + extension, is_last_child)


def run_api_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI server"""
    uvicorn.run(app, host=host, port=port)


def main():
    """Main CLI function with unified multi-mode support"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Datadog Docs Scraper - Multi-mode scraper with RAG export',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # CLI scraping mode (default)
  python main.py --max-depth 3 --delay 1.0
  
  # Content extraction mode (full page content)
  python main.py --extract-content --max-depth 2 --output-dir ./scraped_content
  
  # RAG export (after scraping)
  python main.py --export-rag all
  python main.py --export-rag jsonl --output-dir ./rag_output
  
  # API server mode
  python main.py --api --port 8000
  
  # Combined: scrape + extract + export
  python main.py --max-depth 3 --extract-content --export-rag all
        """
    )
    
    # Mode selection
    parser.add_argument('--api', action='store_true', 
                       help='Run as API server (default: CLI mode)')
    parser.add_argument('--extract-content', action='store_true',
                       help='Extract full page content (not just URLs)')
    
    # RAG export options
    parser.add_argument('--export-rag', choices=['jsonl', 'markdown', 'json', 'all'],
                       help='Export in RAG-optimized format')
    
    # Scraping options
    parser.add_argument('--max-depth', type=int, default=2,
                       help='Maximum depth for scraping (default: 2)')
    parser.add_argument('--delay', type=float, default=0.5,
                       help='Delay between requests in seconds (default: 0.5)')
    parser.add_argument('--output-dir', type=str, default='output',
                       help='Output directory for results (default: output)')
    parser.add_argument('--save-results', action='store_true', default=True,
                       help='Save results to files (default: True)')
    
    # API server options
    parser.add_argument('--port', type=int, default=8000,
                       help='Port for API server (default: 8000)')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                       help='Host for API server (default: 0.0.0.0)')
    
    args = parser.parse_args()

    # Environment variable override (Docker compatibility)
    env_max_depth = os.getenv('MAX_DEPTH')
    if env_max_depth:
        args.max_depth = int(env_max_depth)

    env_delay = os.getenv('DELAY')
    if env_delay:
        args.delay = float(env_delay)

    env_host = os.getenv('HOST')
    if env_host:
        args.host = env_host

    env_port = os.getenv('PORT')
    if env_port:
        args.port = int(env_port)
    
    # Execute based on mode
    if args.api:
        # API server mode
        print(f"🚀 Starting Datadog Scraper API server on {args.host}:{args.port}")
        print(f"📖 API documentation: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}/docs")
        print(f"💚 Health check: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}/health")
        print("="*80)
        run_api_server(args.host, args.port)
    
    elif args.extract_content:
        # Content extraction mode
        print("🔍 Content Extraction Mode")
        print("="*80)
        print(f"📊 Max Depth: {args.max_depth}")
        print(f"⏱️  Delay: {args.delay}s")
        print(f"📁 Output: {args.output_dir}")
        print("="*80 + "\n")
        
        base_url = "https://docs.datadoghq.com/"
        scraper_instance = DatadogDocsScraper(
            base_url=base_url,
            max_depth=args.max_depth,
            delay=args.delay
        )
        extractor = ContentExtractor()
        
        # Run scraping
        print("Starting recursive scrape...")
        start_time = time.time()
        scraper_instance.scrape_recursive(base_url)
        elapsed = time.time() - start_time
        
        print(f"\n✅ Scraping completed in {elapsed:.2f}s - {len(scraper_instance.visited)} URLs found")
        
        # Extract content for each URL
        print("\n📄 Extracting full page content...")
        content_dir = os.path.join(args.output_dir, 'content')
        os.makedirs(content_dir, exist_ok=True)
        
        extracted = []
        for i, url in enumerate(sorted(scraper_instance.visited), 1):
            print(f"  [{i}/{len(scraper_instance.visited)}] {url}")
            content = extractor.extract_content(url)
            extracted.append(content)
            time.sleep(args.delay)
        
        # Save extracted content
        content_file = os.path.join(content_dir, 'extracted_content.json')
        with open(content_file, 'w', encoding='utf-8') as f:
            json.dump(extracted, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Extracted {len(extracted)} pages to {content_file}")
        
        # Save standard results
        if args.save_results:
            scraper_instance.save_results()
        
        # Auto-export to RAG if requested
        if args.export_rag:
            print("\n📦 Exporting to RAG formats...")
            exporter = RAGExporter(scraper_instance)
            if args.export_rag == 'all':
                exporter.export_all(args.output_dir)
            elif args.export_rag == 'jsonl':
                exporter.save_jsonl(f'{args.output_dir}/datadog_rag.jsonl')
            elif args.export_rag == 'markdown':
                exporter.save_markdown(f'{args.output_dir}/datadog_markdown')
            elif args.export_rag == 'json':
                exporter.save_enhanced_json(f'{args.output_dir}/datadog_rag_enhanced.json')
    
    elif args.export_rag:
        # RAG export only (requires existing scraped data)
        print("📦 RAG Export Mode")
        print("="*80)
        
        # Load existing scraper data
        base_url = "https://docs.datadoghq.com/"
        scraper_instance = DatadogDocsScraper(base_url=base_url)
        scraper_instance.scrape_recursive(base_url)
        
        exporter = RAGExporter(scraper_instance)
        
        print(f"Exporting {len(scraper_instance.visited)} URLs in '{args.export_rag}' format...\n")
        
        if args.export_rag == 'all':
            exporter.export_all(args.output_dir)
        elif args.export_rag == 'jsonl':
            exporter.save_jsonl(f'{args.output_dir}/datadog_rag.jsonl')
        elif args.export_rag == 'markdown':
            exporter.save_markdown(f'{args.output_dir}/datadog_markdown')
        elif args.export_rag == 'json':
            exporter.save_enhanced_json(f'{args.output_dir}/datadog_rag_enhanced.json')
    
    else:
        # Default CLI scraping mode
        base_url = "https://docs.datadoghq.com/"
        
        print("🔗 CLI Scraping Mode")
        print("="*80)
        print(f"Base URL: {base_url}")
        print(f"📊 Max Depth: {args.max_depth}")
        print(f"⏱️  Delay: {args.delay}s")
        print(f"💾 Save Results: {args.save_results}")
        print("="*80 + "\n")
        
        scraper_instance = DatadogDocsScraper(
            base_url=base_url,
            max_depth=args.max_depth,
            delay=args.delay
        )
        
        print("Starting recursive scrape...\n")
        start_time = time.time()
        scraper_instance.scrape_recursive(base_url)
        elapsed_time = time.time() - start_time
        
        print("\n" + "="*80)
        print(f"✅ Scraping completed in {elapsed_time:.2f} seconds")
        print(f"📊 Total unique links found: {len(scraper_instance.visited)}")
        print("="*80 + "\n")
        
        if args.save_results:
            scraper_instance.save_results()
            
            # Save tree structure
            with open('datadog_tree_structure.txt', 'w', encoding='utf-8') as f:
                import sys
                old_stdout = sys.stdout
                sys.stdout = f
                print(f"Link Tree Structure for {base_url}")
                print("="*80 + "\n")
                print_tree(scraper_instance, scraper_instance.normalize_url(base_url))
                sys.stdout = old_stdout
            
            print("Tree structure saved to: datadog_tree_structure.txt")
        
        # Display first 20 links as preview
        print("\nPreview (first 20 links):")
        print("-"*80)
        for i, url in enumerate(sorted(scraper_instance.visited)[:20], 1):
            print(f"{i}. {url}")

        if len(scraper_instance.visited) > 20:
            print(f"\n... and {len(scraper_instance.visited) - 20} more links")
        
        # Auto-export if requested
        if args.export_rag:
            print("\n📦 Exporting to RAG formats...")
            exporter = RAGExporter(scraper_instance)
            if args.export_rag == 'all':
                exporter.export_all(args.output_dir)
            elif args.export_rag == 'jsonl':
                exporter.save_jsonl(f'{args.output_dir}/datadog_rag.jsonl')
            elif args.export_rag == 'markdown':
                exporter.save_markdown(f'{args.output_dir}/datadog_markdown')
            elif args.export_rag == 'json':
                exporter.save_enhanced_json(f'{args.output_dir}/datadog_rag_enhanced.json')



if __name__ == "__main__":
    main()