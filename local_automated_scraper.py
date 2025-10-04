#!/usr/bin/env python3
"""
Local Automated Scraper - Alternative to GitHub Actions
Provides the same functionality as the GitHub workflow but runs locally
"""

import os
import sys
import argparse
import subprocess
import shutil
import json
import time
from datetime import datetime
from pathlib import Path

class LocalAutomatedScraper:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.output_dir = self.base_dir / "local_scraped_data"
        self.archives_dir = self.base_dir / "archives"
        
    def setup_directories(self):
        """Create necessary directories"""
        self.output_dir.mkdir(exist_ok=True)
        self.archives_dir.mkdir(exist_ok=True)
        print(f"📁 Created output directory: {self.output_dir}")
        
    def run_scraper(self, max_depth=3, delay=0.3, format_type="both", parallel=True):
        """Run the comprehensive scraper with specified parameters"""
        print(f"🚀 Starting Datadog Documentation Scraping...")
        print(f"📊 Max Depth: {max_depth}")
        print(f"⏱️ Delay: {delay} seconds")
        print(f"📝 Format: {format_type}")
        print(f"⚡ Parallel: {parallel}")
        print("=" * 50)
        
        # Build command
        cmd = [
            sys.executable, "comprehensive_scraper.py",
            "--mode", "comprehensive",
            "--max-depth", str(max_depth),
            "--delay", str(delay),
            "--output-dir", str(self.output_dir)
        ]
        
        if parallel:
            cmd.append("--parallel")
        else:
            cmd.append("--sequential")
            
        # Run the scraper
        start_time = time.time()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.base_dir)
            if result.returncode != 0:
                print(f"❌ Scraper failed with error:")
                print(result.stderr)
                return False
            else:
                print(f"✅ Scraper completed successfully!")
                print(result.stdout)
        except Exception as e:
            print(f"❌ Error running scraper: {e}")
            return False
            
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏱️ Total scraping time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        return True
        
    def generate_summary(self, max_depth, delay, parallel):
        """Generate scraping summary"""
        summary_file = self.output_dir / "SUMMARY.md"
        
        summary_content = f"""# 📊 SCRAPING COMPLETED - SUMMARY
================================

**Scraping Parameters:**
- Max Depth: {max_depth}
- Delay: {delay}s
- Parallel Processing: {parallel}
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Local Run: True

**Files Generated:**
"""

        # Count files
        if (self.output_dir / "json").exists():
            json_count = len(list((self.output_dir / "json").glob("*.json")))
            summary_content += f"- JSON files: {json_count}\n"
            
        if (self.output_dir / "markdown").exists():
            md_count = len(list((self.output_dir / "markdown").glob("*.md")))
            summary_content += f"- Markdown files: {md_count}\n"
            
        # Directory size
        total_size = self.get_directory_size(self.output_dir)
        summary_content += f"- Total size: {total_size}\n\n"
        
        # Add directory structure
        summary_content += "**Directory Structure:**\n```\n"
        summary_content += self.get_directory_tree(self.output_dir, max_depth=3)
        summary_content += "\n```\n"
        
        with open(summary_file, 'w') as f:
            f.write(summary_content)
            
        print(f"📊 Summary generated: {summary_file}")
        return summary_file
        
    def create_archives(self):
        """Create compressed archives"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        archives_created = []
        
        # Create JSON archive
        if (self.output_dir / "json").exists():
            json_archive = self.archives_dir / f"datadog-docs-json-{timestamp}.tar.gz"
            self.create_tar_archive(json_archive, [
                self.output_dir / "json",
                self.output_dir / "combined" if (self.output_dir / "combined").exists() else None,
                self.output_dir / "SUMMARY.md"
            ])
            archives_created.append(json_archive)
            print(f"📦 Created JSON archive: {json_archive}")
            
        # Create Markdown archive
        if (self.output_dir / "markdown").exists():
            md_archive = self.archives_dir / f"datadog-docs-markdown-{timestamp}.tar.gz"
            self.create_tar_archive(md_archive, [
                self.output_dir / "markdown",
                self.output_dir / "combined" if (self.output_dir / "combined").exists() else None,
                self.output_dir / "SUMMARY.md"
            ])
            archives_created.append(md_archive)
            print(f"📦 Created Markdown archive: {md_archive}")
            
        # Create complete archive
        complete_archive = self.archives_dir / f"datadog-docs-complete-{timestamp}.tar.gz"
        self.create_tar_archive(complete_archive, [self.output_dir])
        archives_created.append(complete_archive)
        print(f"📦 Created complete archive: {complete_archive}")
        
        return archives_created
        
    def create_tar_archive(self, archive_path, source_paths):
        """Create a tar.gz archive from source paths"""
        import tarfile
        
        with tarfile.open(archive_path, 'w:gz') as tar:
            for path in source_paths:
                if path and path.exists():
                    if path.is_dir():
                        tar.add(path, arcname=path.name)
                    else:
                        tar.add(path, arcname=path.name)
                        
    def get_directory_size(self, path):
        """Get human-readable directory size"""
        total_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total_size < 1024.0:
                return f"{total_size:.1f}{unit}"
            total_size /= 1024.0
        return f"{total_size:.1f}TB"
        
    def get_directory_tree(self, path, max_depth=3, current_depth=0):
        """Get directory tree structure"""
        if current_depth >= max_depth:
            return ""
            
        tree = ""
        indent = "  " * current_depth
        
        try:
            items = sorted(path.iterdir())
            for item in items[:10]:  # Limit to first 10 items
                if item.is_dir():
                    tree += f"{indent}{item.name}/\n"
                    if current_depth < max_depth - 1:
                        tree += self.get_directory_tree(item, max_depth, current_depth + 1)
                else:
                    tree += f"{indent}{item.name}\n"
                    
            if len(list(path.iterdir())) > 10:
                tree += f"{indent}... ({len(list(path.iterdir())) - 10} more items)\n"
                
        except PermissionError:
            tree += f"{indent}[Permission Denied]\n"
            
        return tree
        
    def run_complete_workflow(self, max_depth=3, delay=0.3, format_type="both", parallel=True):
        """Run the complete scraping workflow"""
        print("🎯 STARTING LOCAL AUTOMATED SCRAPING WORKFLOW")
        print("=" * 60)
        
        # Step 1: Setup
        self.setup_directories()
        
        # Step 2: Run scraper
        success = self.run_scraper(max_depth, delay, format_type, parallel)
        if not success:
            print("❌ Scraping failed, aborting workflow")
            return False
            
        # Step 3: Generate summary
        self.generate_summary(max_depth, delay, parallel)
        
        # Step 4: Create archives
        archives = self.create_archives()
        
        # Step 5: Final report
        print("\n🎉 LOCAL SCRAPING WORKFLOW COMPLETED!")
        print("=" * 60)
        print("📊 Final Statistics:")
        
        if (self.output_dir / "combined" / "statistics.json").exists():
            with open(self.output_dir / "combined" / "statistics.json") as f:
                stats = json.load(f)
                print(json.dumps(stats, indent=2))
                
        print(f"\n📁 Output directory: {self.output_dir}")
        print(f"📦 Archives created: {len(archives)}")
        for archive in archives:
            size = archive.stat().st_size / (1024 * 1024)  # MB
            print(f"  - {archive.name} ({size:.1f} MB)")
            
        print(f"\n💾 Total output size: {self.get_directory_size(self.output_dir)}")
        print(f"📂 Archives location: {self.archives_dir}")
        
        print("\n🔗 Your scraped data is ready!")
        print(f"   Data: {self.output_dir}")
        print(f"   Archives: {self.archives_dir}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description="Local Automated Datadog Documentation Scraper")
    parser.add_argument('--max-depth', type=int, default=3, choices=[1, 2, 3, 4],
                        help='Maximum scraping depth (1-4)')
    parser.add_argument('--delay', type=float, default=0.3,
                        help='Delay between requests (seconds)')
    parser.add_argument('--format', choices=['json', 'markdown', 'both'], default='both',
                        help='Output format')
    parser.add_argument('--parallel', action='store_true', default=True,
                        help='Use parallel processing')
    parser.add_argument('--sequential', action='store_true',
                        help='Use sequential processing (overrides --parallel)')
    
    args = parser.parse_args()
    
    # Handle parallel/sequential
    parallel = args.parallel and not args.sequential
    
    # Create scraper instance
    scraper = LocalAutomatedScraper()
    
    # Run workflow
    success = scraper.run_complete_workflow(
        max_depth=args.max_depth,
        delay=args.delay,
        format_type=args.format,
        parallel=parallel
    )
    
    if success:
        print("\n✅ Workflow completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Workflow failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()