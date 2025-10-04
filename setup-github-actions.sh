#!/bin/bash

# GitHub Actions Setup Helper Script
# This script helps you set up and test the GitHub Actions workflow

set -e

echo "🤖 GitHub Actions Setup Helper for Datadog Scraper"
echo "=================================================="

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a Git repository"
    echo "   Please run this script from your repository root"
    exit 1
fi

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI not found. Install from: https://cli.github.com/"
    echo "   You can still use the web interface to trigger workflows"
fi

echo ""
echo "📁 Checking workflow files..."

# Check if workflow file exists
if [ -f ".github/workflows/datadog-scraper.yml" ]; then
    echo "✅ Workflow file found: .github/workflows/datadog-scraper.yml"
else
    echo "❌ Workflow file missing!"
    echo "   Please ensure .github/workflows/datadog-scraper.yml exists"
    exit 1
fi

# Check if main scripts exist
if [ -f "main.py" ] && [ -f "comprehensive_scraper.py" ]; then
    echo "✅ Scraper scripts found"
else
    echo "❌ Missing scraper scripts (main.py or comprehensive_scraper.py)"
    exit 1
fi

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "✅ Requirements file found"
else
    echo "⚠️  requirements.txt not found - creating one..."
    cat > requirements.txt << EOF
requests>=2.31.0
beautifulsoup4>=4.12.0
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.4.0
EOF
    echo "✅ Created requirements.txt"
fi

echo ""
echo "🔧 Repository Setup Check..."

# Check if repository is on GitHub
REPO_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [[ $REPO_URL == *"github.com"* ]]; then
    echo "✅ GitHub repository detected"
    
    # Extract repo info
    REPO_INFO=$(echo $REPO_URL | sed -E 's/.*github\.com[:/]([^/]+)\/([^/.]+)(\.git)?/\1\/\2/')
    echo "   Repository: $REPO_INFO"
else
    echo "❌ Not a GitHub repository"
    echo "   GitHub Actions only work with GitHub repositories"
    exit 1
fi

echo ""
echo "🚀 Ready to Deploy!"
echo "=================="

echo "📋 Next Steps:"
echo ""
echo "1. 📤 COMMIT AND PUSH to GitHub:"
echo "   git add ."
echo "   git commit -m 'Add GitHub Actions workflow for scraping'"
echo "   git push origin main"
echo ""

if command -v gh &> /dev/null; then
    echo "2. 🎯 TRIGGER WORKFLOW (GitHub CLI):"
    echo "   gh workflow run datadog-scraper.yml \\"
    echo "     --field max_depth=3 \\"
    echo "     --field delay=0.3 \\"
    echo "     --field format=both \\"
    echo "     --field parallel=true"
    echo ""
    echo "3. 📊 MONITOR PROGRESS:"
    echo "   gh run list --workflow=datadog-scraper.yml"
    echo "   gh run watch"
    echo ""
    echo "4. 📥 DOWNLOAD RESULTS:"
    echo "   gh run download --name='datadog-docs-complete-*'"
    echo ""
fi

echo "🌐 ALTERNATIVE: Use GitHub Web Interface:"
echo "   1. Go to: https://github.com/$REPO_INFO/actions"
echo "   2. Click 'Datadog Documentation Scraper'"
echo "   3. Click 'Run workflow'"
echo "   4. Configure settings and run"
echo "   5. Download artifacts when complete"
echo ""

echo "⚙️  WORKFLOW CONFIGURATION OPTIONS:"
echo "   • Max Depth: 1-4 (recommended: 3)"
echo "   • Delay: 0.1-1.0 seconds (recommended: 0.3)"
echo "   • Format: json, markdown, or both"
echo "   • Parallel: true for speed, false for safety"
echo ""

echo "📊 EXPECTED RESULTS:"
echo "   • Depth 1: ~50 URLs, ~8MB, 5 minutes"
echo "   • Depth 2: ~200 URLs, ~40MB, 15 minutes"
echo "   • Depth 3: ~1000 URLs, ~250MB, 45 minutes"
echo "   • Depth 4: ~5000 URLs, ~1.3GB, 3 hours"
echo ""

read -p "🤔 Do you want to commit and push the workflow now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Committing and pushing..."
    
    git add .github/workflows/datadog-scraper.yml
    git add GITHUB_ACTIONS_GUIDE.md
    git add requirements.txt 2>/dev/null || true
    
    git commit -m "Add GitHub Actions workflow for automated Datadog documentation scraping

Features:
- Manual and scheduled triggers
- Configurable depth, delay, and format options
- Parallel processing support
- Multiple artifact formats (JSON, Markdown, archives)
- Automatic summary generation
- 30-90 day artifact retention"
    
    git push origin main
    
    echo "✅ Workflow deployed to GitHub!"
    echo ""
    echo "🎯 Now you can:"
    
    if command -v gh &> /dev/null; then
        echo "   Run: gh workflow run datadog-scraper.yml"
        echo "   Or visit: https://github.com/$REPO_INFO/actions"
    else
        echo "   Visit: https://github.com/$REPO_INFO/actions"
        echo "   Click 'Datadog Documentation Scraper' → 'Run workflow'"
    fi
    
else
    echo "⏸️  Skipped commit/push. Don't forget to push your changes!"
    echo "   git add . && git commit -m 'Add scraping workflow' && git push"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo "Your GitHub Actions workflow is ready to scrape Datadog documentation"
echo "and provide downloadable artifacts with the complete dataset!"
echo ""
echo "📖 For detailed usage instructions, see: GITHUB_ACTIONS_GUIDE.md"