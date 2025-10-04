import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json
import threading
import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

# API imports
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn


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
        try:
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

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []

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

    try:
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

    except Exception as e:
        scraper.is_scraping = False
        raise e


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

    if scraper.is_scraping:
        raise HTTPException(status_code=409, detail="Scraping already in progress")

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

    if not scraper.results:
        raise HTTPException(status_code=404, detail="No results available. Run scraping first.")

    return JSONResponse(content=scraper.results)


@app.get("/results/json")
async def download_json():
    """Download results as JSON file"""

    if not scraper.results:
        raise HTTPException(status_code=404, detail="No results available")

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
        if scraper.is_scraping:
            return {"status": "error", "message": "Scraping already in progress"}

        threading.Thread(target=run_scraping, daemon=True).start()

        return {
            "status": "success",
            "message": "Scraping started via webhook",
            "timestamp": datetime.now().isoformat()
        }

    elif payload.action == "get_results":
        if not scraper.results:
            return {"status": "error", "message": "No results available"}

        return {
            "status": "success",
            "data": scraper.results,
            "timestamp": datetime.now().isoformat()
        }

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {payload.action}")


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
    """Main CLI function"""
    import argparse

    parser = argparse.ArgumentParser(description='Datadog Documentation Scraper')
    parser.add_argument('--api', action='store_true', help='Run as API server')
    parser.add_argument('--host', default='0.0.0.0', help='API server host')
    parser.add_argument('--port', type=int, default=8000, help='API server port')
    parser.add_argument('--max-depth', type=int, default=2, help='Maximum scraping depth')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between requests')

    args = parser.parse_args()

    # Override with environment variables if provided
    env_max_depth = os.getenv('MAX_DEPTH')
    if env_max_depth:
        try:
            args.max_depth = int(env_max_depth)
        except ValueError:
            print(f"Warning: Invalid MAX_DEPTH value '{env_max_depth}', using default")

    env_delay = os.getenv('DELAY')
    if env_delay:
        try:
            args.delay = float(env_delay)
        except ValueError:
            print(f"Warning: Invalid DELAY value '{env_delay}', using default")

    env_host = os.getenv('HOST')
    if env_host:
        args.host = env_host

    env_port = os.getenv('PORT')
    if env_port:
        try:
            args.port = int(env_port)
        except ValueError:
            print(f"Warning: Invalid PORT value '{env_port}', using default")

    if args.api:
        print("Starting Datadog Scraper API Server...")
        print(f"API Docs available at: http://{args.host}:{args.port}/docs")
        print(f"Health check: http://{args.host}:{args.port}/health")
        print("="*80)
        run_api_server(args.host, args.port)
    else:
        # Original CLI behavior
        base_url = "https://docs.datadoghq.com/"

        print("Datadog Documentation Link Scraper")
        print("="*80)
        print(f"Base URL: {base_url}")
        print("\nConfiguration:")
        print(f"  - Max Depth: {args.max_depth} (adjust as needed)")
        print(f"  - Delay: {args.delay}s between requests")
        print("\nNote: Deeper scraping will take longer. Start with depth 1-2.")
        print("="*80 + "\n")

        # Create scraper instance
        scraper_instance = DatadogDocsScraper(
            base_url=base_url,
            max_depth=args.max_depth,
            delay=args.delay
        )

        # Start scraping
        print("Starting recursive scrape...\n")
        start_time = time.time()

        scraper_instance.scrape_recursive(base_url)

        elapsed_time = time.time() - start_time

        # Display summary
        print("\n" + "="*80)
        print(f"Scraping completed in {elapsed_time:.2f} seconds")
        print(f"Total unique links found: {len(scraper_instance.visited)}")
        print("="*80 + "\n")

        # Save results
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


if __name__ == "__main__":
    main()