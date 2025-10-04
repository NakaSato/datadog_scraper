#!/usr/bin/env python3
"""
Demo script to show the difference between shallow and deep scraping
"""

import sys
import os
sys.path.append('.')

from main import DatadogDocsScraper

def compare_depths():
    """Compare URL discovery at different depths"""
    base_url = "https://docs.datadoghq.com/"
    
    print("🔍 Comparing Scraping Depths - How many URLs we discover:")
    print("="*80)
    
    depths = [1, 2, 3]
    results = {}
    
    for depth in depths:
        print(f"\n📊 Testing depth {depth}...")
        scraper = DatadogDocsScraper(base_url=base_url, max_depth=depth, delay=0.2)
        scraper.scrape_recursive(base_url)
        
        results[depth] = len(scraper.visited)
        print(f"   Depth {depth}: {len(scraper.visited)} URLs found")
        
        # Show some sample URLs
        sample_urls = sorted(list(scraper.visited))[:5]
        for url in sample_urls:
            print(f"     • {url}")
        if len(scraper.visited) > 5:
            print(f"     ... and {len(scraper.visited) - 5} more")
    
    print(f"\n📈 RESULTS COMPARISON:")
    print("="*80)
    for depth in depths:
        print(f"Depth {depth}: {results[depth]:4d} URLs")
    
    print(f"\n💡 RECOMMENDATIONS FOR COMPLETE DATA:")
    print(f"   • Depth 1: {results[1]} URLs - Good for quick overview")
    print(f"   • Depth 2: {results[2]} URLs - Better coverage") 
    print(f"   • Depth 3: {results[3]} URLs - Most complete data")
    print(f"   • Depth 3 finds {results[3]/results[1]:.1f}x more URLs than depth 1!")
    
    return results

if __name__ == "__main__":
    compare_depths()