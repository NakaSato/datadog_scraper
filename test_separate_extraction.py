#!/usr/bin/env python3
"""
Test script to demonstrate separate file extraction functionality
"""

import sys
import os
sys.path.append('.')

from main import ContentExtractor

def test_separate_extraction():
    """Test the separate file extraction with a few URLs"""
    
    # Test URLs (just a few for demo)
    test_urls = [
        "https://docs.datadoghq.com/",
        "https://docs.datadoghq.com/getting_started/",
        "https://docs.datadoghq.com/api/"
    ]
    
    extractor = ContentExtractor()
    
    # Test JSON format
    print("Testing JSON format extraction...")
    json_stats = extractor.save_as_separate_files(
        urls=test_urls,
        output_dir='./demo_extraction/json',
        format_type='json',
        delay=0.3
    )
    
    print(f"JSON Stats: {json_stats}")
    
    # Test Markdown format
    print("\nTesting Markdown format extraction...")
    md_stats = extractor.save_as_separate_files(
        urls=test_urls,
        output_dir='./demo_extraction/markdown',
        format_type='markdown',
        delay=0.3
    )
    
    print(f"Markdown Stats: {md_stats}")
    
    # Show created files
    print("\nCreated files:")
    for root, dirs, files in os.walk('./demo_extraction'):
        for file in files:
            filepath = os.path.join(root, file)
            print(f"  {filepath}")
    
    print("\nDemo complete! Check ./demo_extraction/ for results")

if __name__ == "__main__":
    test_separate_extraction()