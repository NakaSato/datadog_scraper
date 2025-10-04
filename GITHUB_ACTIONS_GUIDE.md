# 🤖 GitHub Actions Automated Scraping

This repository includes a GitHub Actions workflow that automatically scrapes Datadog documentation and saves the results as downloadable artifacts.

## 🚀 Quick Start

### Option 1: Manual Trigger (Recommended)

1. **Go to Actions tab** in your GitHub repository
2. **Select "Datadog Documentation Scraper"** workflow
3. **Click "Run workflow"**
4. **Configure settings:**
   - **Max Depth**: `3` (recommended for complete data)
   - **Delay**: `0.3` seconds (balance speed vs. server respect)
   - **Format**: `both` (JSON + Markdown)
   - **Parallel**: `true` (faster processing)
5. **Click "Run workflow"**

### Option 2: Automatic Triggers

The workflow automatically runs:
- **Weekly** on Sundays at 2 AM UTC
- **On push** to main branch (when scraper files change)

## 📦 What You Get

### Artifacts (Available for 30-90 days)

After the workflow completes, you can download:

1. **`datadog-docs-json-{run_number}`**
   - All individual JSON files
   - Combined dataset
   - Summary report

2. **`datadog-docs-markdown-{run_number}`**
   - All individual Markdown files
   - Combined dataset  
   - Summary report

3. **`datadog-docs-complete-{run_number}`**
   - Everything (JSON + Markdown + combined)
   - Complete dataset
   - Summary and statistics

4. **`datadog-docs-archives-{run_number}`**
   - Compressed `.tar.gz` files
   - Smaller download size
   - Long-term storage (90 days)

### File Structure

```
scraped_data/
├── json/                    # Individual JSON files per URL
│   ├── index.json
│   ├── api-*.json
│   └── ... (hundreds/thousands of files)
├── markdown/                # Individual Markdown files per URL  
│   ├── index.md
│   ├── api-*.md
│   └── ... (hundreds/thousands of files)
├── combined/                # Combined datasets
│   ├── all_content.json    # All pages in single file
│   ├── all_urls.txt        # Complete URL list
│   └── statistics.json     # Scraping statistics
└── SUMMARY.md              # Workflow summary report
```

## ⚙️ Configuration Options

### Scraping Depth
- **Depth 1**: ~50 URLs (quick overview)
- **Depth 2**: ~200 URLs (good coverage)
- **Depth 3**: ~1000+ URLs (complete coverage) ⭐ **Recommended**
- **Depth 4**: ~5000+ URLs (maximum coverage, takes hours)

### Processing Speed
- **Delay 0.1s**: Fastest (risk of rate limiting)
- **Delay 0.3s**: Balanced ⭐ **Recommended**
- **Delay 0.5s**: Safest (slower but respectful)

### Processing Mode
- **Parallel**: 3x faster (recommended for large datasets)
- **Sequential**: Safer (use if parallel fails)

## 📥 How to Download Results

### From GitHub Web Interface

1. **Go to Actions tab** in your repository
2. **Click on the completed workflow run**
3. **Scroll down to "Artifacts" section**
4. **Click to download** any artifact (will download as ZIP)
5. **Extract the ZIP** to access your scraped data

### Using GitHub CLI

```bash
# List available artifacts
gh run list --workflow="datadog-scraper.yml"

# Download specific artifact  
gh run download RUN_ID --name="datadog-docs-complete-123"

# Download all artifacts from latest run
gh run download --name="datadog-docs-complete-*"
```

### Using REST API

```bash
# Get latest workflow run
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO/actions/workflows/datadog-scraper.yml/runs

# Download specific artifact (requires additional API calls)
```

## 🔧 Advanced Usage

### Custom Workflow Triggers

Add to `.github/workflows/datadog-scraper.yml`:

```yaml
on:
  # Daily at 3 AM
  schedule:
    - cron: '0 3 * * *'
    
  # On specific branches
  push:
    branches: [ main, develop ]
    
  # On releases
  release:
    types: [created]
```

### Environment Variables

Set in repository secrets for advanced configuration:

- `SCRAPING_DELAY`: Override default delay
- `MAX_WORKERS`: Parallel processing workers
- `CUSTOM_BASE_URL`: Scrape different documentation site

### Workflow Modifications

Edit `.github/workflows/datadog-scraper.yml` to:

- Change retention periods (7-90 days)
- Add different output formats
- Integrate with external storage (S3, etc.)
- Send notifications (Slack, email)
- Run different scraping modes

## 📊 Monitoring & Logs

### View Progress

1. **Go to Actions tab**
2. **Click on running workflow**
3. **Click on job name** to see live logs
4. **Monitor progress** in real-time

### Log Sections

- **Setup**: Python installation, dependencies
- **Scraping**: URL discovery progress
- **Extraction**: Content extraction progress
- **Packaging**: Archive creation
- **Upload**: Artifact upload status

## 🛠️ Troubleshooting

### Common Issues

**Workflow Times Out (6 hours)**
- Reduce max depth (3→2 or 2→1)
- Increase delay (0.3→0.5s)
- Use sequential processing

**Rate Limiting Errors**
- Increase delay between requests
- Use sequential instead of parallel
- Add random delays

**Out of Disk Space**
- GitHub Actions runners have ~14GB available
- For very large datasets, consider streaming to external storage

**Artifacts Too Large**
- Split into smaller chunks
- Use compression
- Store only essential formats

### Debug Mode

Add to workflow for detailed debugging:

```yaml
- name: Debug scraping
  run: |
    python comprehensive_scraper.py --help
    python -c "import requests; print(requests.__version__)"
    df -h  # Check disk space
```

## 🔐 Security & Rate Limits

### Best Practices

- **Respectful delays**: Don't set below 0.1s
- **Monitor usage**: Check for rate limiting
- **Reasonable depth**: Depth 4+ can take many hours
- **Resource limits**: GitHub Actions has usage limits

### Rate Limiting

- **Free accounts**: 2,000 minutes/month
- **Workflow timeout**: 6 hours maximum
- **Concurrent jobs**: Limited by plan
- **Artifact storage**: 500MB-2GB limits

## 🚀 Quick Examples

### Lightweight Daily Scraping
```yaml
# Add to workflow triggers
schedule:
  - cron: '0 6 * * *'  # Daily 6 AM

# Use in manual trigger
max_depth: '2'
delay: '0.5'
parallel: false
```

### Maximum Coverage Weekly
```yaml
# Add to workflow triggers  
schedule:
  - cron: '0 2 * * 0'  # Sunday 2 AM

# Use in manual trigger
max_depth: '4'
delay: '0.2' 
parallel: true
```

### Emergency Quick Scrape
```yaml
# Manual trigger settings
max_depth: '1'
delay: '0.1'
format: 'json'
parallel: true
```

## 📈 Expected Results

### Typical Dataset Sizes

| Depth | URLs | JSON Size | MD Size | Total | Time |
|-------|------|-----------|---------|-------|------|
| 1     | ~50  | ~5MB      | ~3MB    | ~8MB  | 5min |
| 2     | ~200 | ~25MB     | ~15MB   | ~40MB | 15min|
| 3     | ~1000| ~150MB    | ~100MB  | ~250MB| 45min|
| 4     | ~5000| ~800MB    | ~500MB  | ~1.3GB| 3hrs |

### File Counts

- **JSON files**: 1 per URL + combined datasets
- **Markdown files**: 1 per URL + structured content
- **Archives**: Compressed versions for download
- **Metadata**: Statistics, summaries, logs

Start with **Depth 3** for the best balance of completeness and time!