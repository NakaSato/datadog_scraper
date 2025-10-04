#!/usr/bin/env python3
"""
Comprehensive Data Scraper

This script demonstrates different approaches to scrape all data from URLs:
1. Complete site scraping with content extraction
2. URL-specific scraping 
3. Category-based scraping
4. Parallel processing for faster extraction
"""

import sys
import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.append('.')

from main import ContentExtractor, DatadogDocsScraper

def extract_content_parallel(urls, extractor, output_dir, delay):
    """Extract content using parallel processing"""
    all_content = []
    
    def extract_single_url(url_info):
        i, url = url_info
        print(f"  [{i}/{len(urls)}] {url}")
        
        content = extractor.extract_content(url)
        filename = extractor._url_to_filename(url)
        
        # Save JSON
        json_path = f"{output_dir}/json/{filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        
        # Save Markdown
        md_path = f"{output_dir}/markdown/{filename}.md"
        md_content = extractor._convert_to_markdown(content)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        time.sleep(delay)  # Still respect rate limiting
        return content
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=3) as executor:
        url_enumerated = list(enumerate(urls, 1))
        future_to_url = {executor.submit(extract_single_url, url_info): url_info for url_info in url_enumerated}
        
        for future in as_completed(future_to_url):
            content = future.result()
            all_content.append(content)
    
    return all_content

def extract_content_sequential(urls, extractor, output_dir, delay):
    """Extract content sequentially (original method)"""
    all_content = []
    
    for i, url in enumerate(urls, 1):
        print(f"  [{i}/{len(urls)}] {url}")
        
        # Extract content
        content = extractor.extract_content(url)
        all_content.append(content)
        
        # Save individual files
        filename = extractor._url_to_filename(url)
        
        # JSON format
        json_path = f"{output_dir}/json/{filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        
        # Markdown format
        md_path = f"{output_dir}/markdown/{filename}.md"
        md_content = extractor._convert_to_markdown(content)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        time.sleep(delay)
    
    return all_content

def scrape_all_comprehensive(max_depth=3, delay=0.3, output_dir="./comprehensive_scrape", parallel=True):
    """
    Comprehensive scraping approach:
    1. First discover all URLs with deeper depth
    2. Then extract content from each URL (optionally in parallel)
    3. Save in multiple formats
    """
    print("🚀 Starting COMPLETE Data Scraping (All URLs)")
    print("="*80)
    print(f"📊 Max Depth: {max_depth} (deeper = more complete)")
    print(f"⚡ Parallel Processing: {parallel}")
    print(f"⏱️  Delay: {delay}s per request")
    print("="*80)
    
    # Step 1: Discover ALL URLs with increased depth
    print("📡 Phase 1: Discovering ALL URLs (this may take a while)...")
    base_url = "https://docs.datadoghq.com/"
    scraper = DatadogDocsScraper(
        base_url=base_url,
        max_depth=max_depth,
        delay=delay
    )
    
    start_time = time.time()
    scraper.scrape_recursive(base_url)
    discovery_time = time.time() - start_time
    
    print(f"✅ Discovered {len(scraper.visited)} URLs in {discovery_time:.2f}s")
    print(f"📈 That's {len(scraper.visited)/discovery_time:.1f} URLs per second!")
    
    # Step 2: Extract content from ALL URLs
    print(f"\n📄 Phase 2: Extracting content from {len(scraper.visited)} URLs...")
    extractor = ContentExtractor()
    
    # Create output directories
    os.makedirs(f"{output_dir}/json", exist_ok=True)
    os.makedirs(f"{output_dir}/markdown", exist_ok=True)
    os.makedirs(f"{output_dir}/combined", exist_ok=True)
    
    # Extract content with progress tracking
    urls = sorted(scraper.visited)
    all_content = []
    
    start_extraction = time.time()
    
    if parallel and len(urls) > 10:
        # Parallel processing for large datasets
        print("⚡ Using parallel processing for faster extraction...")
        all_content = extract_content_parallel(urls, extractor, output_dir, delay)
    else:
        # Sequential processing
        print("🔄 Using sequential processing...")
        all_content = extract_content_sequential(urls, extractor, output_dir, delay)
    
    extraction_time = time.time() - start_extraction
    
    # Step 3: Save combined data
    print(f"\n💾 Phase 3: Saving combined datasets...")
    
    # Combined JSON
    with open(f"{output_dir}/combined/all_content.json", 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'total_pages': len(all_content),
                'base_url': base_url,
                'max_depth': max_depth,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'discovery_time': discovery_time,
                'extraction_time': extraction_time,
                'total_time': discovery_time + extraction_time
            },
            'pages': all_content
        }, f, indent=2, ensure_ascii=False)
    
    # URL list
    with open(f"{output_dir}/combined/all_urls.txt", 'w', encoding='utf-8') as f:
        f.write(f"All Scraped URLs from {base_url}\n")
        f.write(f"Total: {len(urls)} URLs\n")
        f.write(f"Scraped: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        for i, url in enumerate(urls, 1):
            f.write(f"{i}. {url}\n")
    
    # Statistics
    stats = {
        'total_urls': len(urls),
        'total_pages_extracted': len(all_content),
        'discovery_time': discovery_time,
        'extraction_time': extraction_time,
        'total_time': discovery_time + extraction_time,
        'average_time_per_page': extraction_time / len(all_content) if all_content else 0,
        'output_directory': output_dir
    }
    
    with open(f"{output_dir}/combined/statistics.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    
    print(f"\n✨ COMPLETE data scraping finished!")
    print(f"📊 Final Statistics:")
    print(f"   • URLs discovered: {stats['total_urls']} (depth {max_depth})")
    print(f"   • Pages extracted: {stats['total_pages_extracted']}")
    print(f"   • Discovery time: {stats['discovery_time']:.2f}s")
    print(f"   • Extraction time: {stats['extraction_time']:.2f}s")
    print(f"   • Total time: {stats['total_time']:.2f}s")
    print(f"   • Avg per page: {stats['average_time_per_page']:.2f}s")
    print(f"   • Processing method: {'Parallel' if parallel else 'Sequential'}")
    print(f"📁 ALL DATA saved to: {output_dir}/")
    print(f"💾 Individual files: {len(urls)} JSON + {len(urls)} Markdown")
    print(f"📦 Combined dataset: all_content.json ({len(all_content)} pages)")
    
    return stats

def scrape_specific_urls(urls, output_dir="./specific_scrape"):
    """Scrape specific URLs provided by user"""
    print(f"🎯 Scraping {len(urls)} specific URLs...")
    
    extractor = ContentExtractor()
    os.makedirs(f"{output_dir}/json", exist_ok=True)
    os.makedirs(f"{output_dir}/markdown", exist_ok=True)
    
    results = []
    for i, url in enumerate(urls, 1):
        print(f"  [{i}/{len(urls)}] {url}")
        
        content = extractor.extract_content(url)
        results.append(content)
        
        filename = extractor._url_to_filename(url)
        
        # Save JSON
        with open(f"{output_dir}/json/{filename}.json", 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        
        # Save Markdown
        md_content = extractor._convert_to_markdown(content)
        with open(f"{output_dir}/markdown/{filename}.md", 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        time.sleep(0.5)
    
    print(f"✅ Scraped {len(results)} URLs to {output_dir}/")
    return results

def scrape_by_category(base_url="https://docs.datadoghq.com/", category_prefix=None, max_depth=1):
    """Scrape URLs that match a specific category/prefix"""
    print(f"📂 Scraping by category: {category_prefix or 'all'}")
    
    scraper = DatadogDocsScraper(base_url=base_url, max_depth=max_depth)
    scraper.scrape_recursive(base_url)
    
    if category_prefix:
        filtered_urls = [url for url in scraper.visited if category_prefix in url]
        print(f"🔍 Found {len(filtered_urls)} URLs matching '{category_prefix}'")
    else:
        filtered_urls = list(scraper.visited)
        print(f"🔍 Found {len(filtered_urls)} total URLs")
    
    return scrape_specific_urls(filtered_urls, f"./category_scrape_{category_prefix or 'all'}")

def scrape_everything(output_dir="./everything_scrape"):
    """Scrape absolutely everything with maximum depth and coverage"""
    print("🌍 SCRAPING EVERYTHING - Maximum Coverage Mode")
    print("="*80)
    print("⚠️  WARNING: This will take a LONG time and scrape thousands of pages!")
    print("⚠️  This may take 2-6 hours depending on the site size.")
    print("="*80)
    
    response = input("Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Cancelled by user")
        return
    
    # Maximum depth scraping
    return scrape_all_comprehensive(
        max_depth=4,  # Very deep
        delay=0.2,    # Faster but still respectful
        output_dir=output_dir,
        parallel=True
    )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Data Scraper - Get ALL the data!")
    parser.add_argument('--mode', choices=['comprehensive', 'specific', 'category', 'everything'], 
                       default='comprehensive', help='Scraping mode')
    parser.add_argument('--max-depth', type=int, default=3, help='Max depth for discovery (default: 3 for complete coverage)')
    parser.add_argument('--delay', type=float, default=0.3, help='Delay between requests (default: 0.3s)')
    parser.add_argument('--output-dir', default='./comprehensive_scrape', help='Output directory')
    parser.add_argument('--category', help='Category prefix to filter URLs')
    parser.add_argument('--urls', nargs='*', help='Specific URLs to scrape')
    parser.add_argument('--parallel', action='store_true', default=True, help='Use parallel processing (default: True)')
    parser.add_argument('--sequential', action='store_true', help='Force sequential processing')
    
    args = parser.parse_args()
    
    # Handle parallel vs sequential
    if args.sequential:
        parallel = False
    else:
        parallel = args.parallel
    
    if args.mode == 'comprehensive':
        scrape_all_comprehensive(args.max_depth, args.delay, args.output_dir, parallel)
    elif args.mode == 'everything':
        scrape_everything(args.output_dir)
    elif args.mode == 'specific' and args.urls:
        scrape_specific_urls(args.urls, args.output_dir)
    elif args.mode == 'category':
        scrape_by_category(category_prefix=args.category, max_depth=args.max_depth)
    else:
        print("❌ Invalid mode or missing arguments")
        print("\n💡 Quick start examples:")
        print("   python comprehensive_scraper.py --mode comprehensive --max-depth 3")
        print("   python comprehensive_scraper.py --mode everything")
        print("   python comprehensive_scraper.py --mode category --category api")
        parser.print_help()