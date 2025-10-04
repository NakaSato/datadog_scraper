#!/bin/bash

# Quick Local Scraper - Immediate Alternative to GitHub Actions
# Runs the same workflow locally with same outputs

echo "🏃‍♂️ QUICK LOCAL SCRAPER"
echo "========================"
echo "Alternative to GitHub Actions - runs locally with same results"
echo ""

# Configuration (modify these as needed)
MAX_DEPTH=${1:-3}
DELAY=${2:-0.3}
FORMAT=${3:-both}
PARALLEL=${4:-true}

echo "📊 Configuration:"
echo "  Max Depth: $MAX_DEPTH"
echo "  Delay: $DELAY seconds"  
echo "  Format: $FORMAT"
echo "  Parallel: $PARALLEL"
echo ""

# Create timestamp for this run
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RUN_DIR="local_run_$TIMESTAMP"

echo "📁 Creating run directory: $RUN_DIR"
mkdir -p "$RUN_DIR"

# Run the comprehensive scraper
echo ""
echo "🚀 Starting scraper..."
if [ "$PARALLEL" = "true" ]; then
    python comprehensive_scraper.py \
        --mode comprehensive \
        --max-depth $MAX_DEPTH \
        --delay $DELAY \
        --output-dir "./$RUN_DIR" \
        --parallel
else
    python comprehensive_scraper.py \
        --mode comprehensive \
        --max-depth $MAX_DEPTH \
        --delay $DELAY \
        --output-dir "./$RUN_DIR" \
        --sequential
fi

# Check if scraping was successful
if [ $? -eq 0 ]; then
    echo "✅ Scraping completed successfully!"
else
    echo "❌ Scraping failed!"
    exit 1
fi

# Generate summary
echo ""
echo "📊 Generating summary..."
cat > "./$RUN_DIR/SUMMARY.md" << EOF
# 📊 LOCAL SCRAPING SUMMARY
==========================

**Run Details:**
- Timestamp: $(date)
- Max Depth: $MAX_DEPTH
- Delay: $DELAY seconds
- Format: $FORMAT
- Parallel: $PARALLEL
- Run Directory: $RUN_DIR

**Files Generated:**
EOF

# Count files
if [ -d "./$RUN_DIR/json" ]; then
    JSON_COUNT=$(find "./$RUN_DIR/json" -name "*.json" | wc -l)
    echo "- JSON files: $JSON_COUNT" >> "./$RUN_DIR/SUMMARY.md"
fi

if [ -d "./$RUN_DIR/markdown" ]; then
    MD_COUNT=$(find "./$RUN_DIR/markdown" -name "*.md" | wc -l)
    echo "- Markdown files: $MD_COUNT" >> "./$RUN_DIR/SUMMARY.md"
fi

# Directory size
TOTAL_SIZE=$(du -sh "./$RUN_DIR" | cut -f1)
echo "- Total size: $TOTAL_SIZE" >> "./$RUN_DIR/SUMMARY.md"

# Create archives
echo ""
echo "📦 Creating archives..."
cd "$RUN_DIR"

# JSON archive
if [ -d "json" ]; then
    tar -czf "../datadog-docs-json-$TIMESTAMP.tar.gz" json/ combined/ SUMMARY.md 2>/dev/null
    echo "✅ Created: datadog-docs-json-$TIMESTAMP.tar.gz"
fi

# Markdown archive  
if [ -d "markdown" ]; then
    tar -czf "../datadog-docs-markdown-$TIMESTAMP.tar.gz" markdown/ combined/ SUMMARY.md 2>/dev/null
    echo "✅ Created: datadog-docs-markdown-$TIMESTAMP.tar.gz"
fi

# Complete archive
cd ..
tar -czf "datadog-docs-complete-$TIMESTAMP.tar.gz" "$RUN_DIR/"
echo "✅ Created: datadog-docs-complete-$TIMESTAMP.tar.gz"

# Final report
echo ""
echo "🎉 LOCAL SCRAPING COMPLETED!"
echo "============================="
echo "📂 Output directory: $RUN_DIR/"
echo "📦 Archives created:"
ls -lh datadog-docs-*-$TIMESTAMP.tar.gz 2>/dev/null
echo ""
echo "📊 Summary available in: $RUN_DIR/SUMMARY.md"
echo ""
echo "🎯 QUICK ACCESS:"
echo "  View summary: cat $RUN_DIR/SUMMARY.md"
echo "  JSON files:   ls $RUN_DIR/json/"
echo "  Markdown:     ls $RUN_DIR/markdown/"
echo "  Combined:     ls $RUN_DIR/combined/"
echo ""
echo "📥 Download archives or use the $RUN_DIR directory directly!"