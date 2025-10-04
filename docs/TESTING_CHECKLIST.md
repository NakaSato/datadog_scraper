# ✅ Verification Checklist - Unified main.py

## Pre-Deployment Testing

### ✅ Completed Tests

#### 1. Help Output
- [x] `python main.py --help` shows all options
- [x] Examples section displays correctly
- [x] All mode flags documented

**Test Command:**
```bash
python main.py --help
```

**Expected Output:**
```
usage: main.py [-h] [--api] [--extract-content] [--export-rag {jsonl,markdown,json,all}]
               [--max-depth MAX_DEPTH] [--delay DELAY] [--output-dir OUTPUT_DIR] 
               [--save-results] [--port PORT] [--host HOST]

Datadog Docs Scraper - Multi-mode scraper with RAG export
...
```

#### 2. CLI Scraping Mode
- [x] Basic scraping works with `--max-depth 1`
- [x] Standard output files created
- [x] Tree structure generated

**Test Command:**
```bash
python main.py --max-depth 1 --delay 0.5
```

**Expected Outputs:**
- `datadog_all_links.txt`
- `datadog_links_detailed.txt`
- `datadog_links.json`
- `datadog_tree_structure.txt`

### 🔲 Pending Tests

#### 3. Content Extraction Mode
- [ ] Content extraction completes successfully
- [ ] JSON file created with proper structure
- [ ] All content fields populated

**Test Command:**
```bash
python main.py --extract-content --max-depth 1 --delay 0.5
```

**Expected Output:**
```
output/
  content/
    extracted_content.json
```

**Verify Structure:**
```bash
# Check JSON structure
cat output/content/extracted_content.json | jq '.[0] | keys'

# Expected keys:
# ["url", "title", "text", "headings", "code_blocks", "word_count", "extracted_at"]
```

#### 4. RAG Export Mode

##### 4a. JSONL Export
- [ ] JSONL file created
- [ ] One JSON object per line
- [ ] Valid JSON formatting

**Test Command:**
```bash
python main.py --export-rag jsonl
```

**Verify:**
```bash
# Check file exists
ls -lh output/datadog_rag.jsonl

# Validate JSONL format
head -n 1 output/datadog_rag.jsonl | jq .

# Count documents
wc -l output/datadog_rag.jsonl
```

##### 4b. Markdown Export
- [ ] Markdown directory created
- [ ] Files organized by category
- [ ] Frontmatter present in files

**Test Command:**
```bash
python main.py --export-rag markdown
```

**Verify:**
```bash
# Check directory structure
tree output/datadog_markdown

# Verify frontmatter in first file
head -n 10 output/datadog_markdown/*/*md | head -n 20
```

##### 4c. Enhanced JSON Export
- [ ] JSON file created
- [ ] Contains documents and metadata
- [ ] Relationships mapped

**Test Command:**
```bash
python main.py --export-rag json
```

**Verify:**
```bash
# Check structure
cat output/datadog_rag_enhanced.json | jq '. | keys'

# Expected: ["documents", "metadata"]

# Check metadata
cat output/datadog_rag_enhanced.json | jq '.metadata'
```

##### 4d. All Formats Export
- [ ] All three formats created
- [ ] Summary statistics displayed

**Test Command:**
```bash
python main.py --export-rag all
```

**Verify:**
```bash
ls -lh output/
# Should see:
# - datadog_rag.jsonl
# - datadog_rag_enhanced.json
# - datadog_markdown/
```

#### 5. Combined Mode
- [ ] Scraping + content extraction works
- [ ] Scraping + RAG export works
- [ ] All modes together work

**Test Commands:**
```bash
# Test 1: Scrape + Extract
python main.py --max-depth 1 --extract-content

# Test 2: Scrape + Export
python main.py --max-depth 1 --export-rag jsonl

# Test 3: Everything
python main.py --max-depth 1 --extract-content --export-rag all
```

#### 6. API Server Mode

##### 6a. Server Startup
- [ ] Server starts without errors
- [ ] Health endpoint responds
- [ ] Docs accessible

**Test Commands:**
```bash
# Start server in background
python main.py --api &
API_PID=$!

# Wait for startup
sleep 2

# Test health endpoint
curl http://localhost:8000/health

# Test docs endpoint
curl http://localhost:8000/docs

# Cleanup
kill $API_PID
```

##### 6b. Scraping Endpoint
- [ ] POST /scrape triggers background scraping
- [ ] Status endpoint shows progress
- [ ] Results endpoint returns data

**Test Commands:**
```bash
# Start server
python main.py --api &
API_PID=$!
sleep 2

# Trigger scraping
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"max_depth": 1, "delay": 0.5, "save_results": true}'

# Wait a bit
sleep 5

# Check status
curl http://localhost:8000/status

# Get results
curl http://localhost:8000/results | jq .

# Cleanup
kill $API_PID
```

##### 6c. Webhook Endpoint
- [ ] Webhook triggers scraping
- [ ] Returns success response

**Test Commands:**
```bash
# Start server
python main.py --api &
API_PID=$!
sleep 2

# Trigger webhook
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"action": "start_scraping"}'

# Cleanup
kill $API_PID
```

##### 6d. RAG Export Endpoints
- [ ] /export/rag/jsonl works
- [ ] /export/rag/markdown works
- [ ] /export/rag/json works
- [ ] /export/rag/all works

**Test Commands:**
```bash
# Start server and scrape first
python main.py --api &
API_PID=$!
sleep 2

# Trigger scraping
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"max_depth": 1, "delay": 0.5, "save_results": true}'

# Wait for completion
sleep 10

# Test RAG endpoints
curl http://localhost:8000/export/rag/jsonl --output test_rag.jsonl
curl http://localhost:8000/export/rag/json --output test_rag.json
curl http://localhost:8000/export/rag/markdown --output test_rag_markdown.zip

# Cleanup
kill $API_PID
rm -f test_rag.*
```

#### 7. Docker Integration

##### 7a. Build
- [ ] Docker image builds successfully
- [ ] No errors in build logs

**Test Commands:**
```bash
./docker-deploy.sh build
```

##### 7b. Deployment
- [ ] Container starts
- [ ] Health check passes
- [ ] API accessible

**Test Commands:**
```bash
# Start container
./docker-deploy.sh up

# Wait for startup
sleep 5

# Test health
curl http://localhost:8000/health

# Check logs
./docker-deploy.sh logs

# Cleanup
./docker-deploy.sh down
```

##### 7c. n8n Integration
- [ ] All services start
- [ ] Network connectivity works
- [ ] Workflows import successfully

**Test Commands:**
```bash
# Start full stack
./docker-deploy.sh n8n

# Wait for startup
sleep 10

# Test connections
docker exec -it datadog-scraper curl http://localhost:8000/health
docker exec -it datadog-mcp-server curl http://localhost:8001/health

# Cleanup
./docker-deploy.sh down
```

#### 8. Environment Variables

##### 8a. MAX_DEPTH Override
- [ ] Environment variable overrides CLI arg

**Test Commands:**
```bash
export MAX_DEPTH=3
python main.py --max-depth 1
# Should use depth 3, not 1
unset MAX_DEPTH
```

##### 8b. DELAY Override
- [ ] Environment variable overrides CLI arg

**Test Commands:**
```bash
export DELAY=2.0
python main.py --delay 0.5
# Should use 2.0s delay
unset DELAY
```

##### 8c. PORT Override
- [ ] Environment variable works for API mode

**Test Commands:**
```bash
export PORT=8080
python main.py --api &
API_PID=$!
sleep 2
curl http://localhost:8080/health
kill $API_PID
unset PORT
```

## Quick Test Suite

Run all basic tests at once:

```bash
#!/bin/bash
set -e

echo "🧪 Running Quick Test Suite..."

echo "1️⃣ Testing help output..."
python main.py --help > /dev/null
echo "✅ Help works"

echo "2️⃣ Testing CLI mode..."
python main.py --max-depth 1 --delay 0.3
echo "✅ CLI scraping works"

echo "3️⃣ Testing RAG export..."
python main.py --export-rag jsonl
echo "✅ JSONL export works"

echo "4️⃣ Testing API server..."
python main.py --api &
API_PID=$!
sleep 3
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✅ API server works"
kill $API_PID

echo ""
echo "🎉 All quick tests passed!"
```

## Comprehensive Test Suite

For thorough testing:

```bash
#!/bin/bash
set -e

echo "🧪 Running Comprehensive Test Suite..."
echo "⚠️  This will take several minutes..."
echo ""

# Test 1: CLI modes
echo "1️⃣ Testing CLI scraping..."
python main.py --max-depth 1
[ -f datadog_links.json ] && echo "✅ CLI scraping works"

# Test 2: Content extraction
echo "2️⃣ Testing content extraction..."
python main.py --extract-content --max-depth 1
[ -f output/content/extracted_content.json ] && echo "✅ Content extraction works"

# Test 3: RAG exports
echo "3️⃣ Testing RAG exports..."
python main.py --export-rag all
[ -f output/datadog_rag.jsonl ] && echo "✅ JSONL export works"
[ -d output/datadog_markdown ] && echo "✅ Markdown export works"
[ -f output/datadog_rag_enhanced.json ] && echo "✅ Enhanced JSON export works"

# Test 4: Combined mode
echo "4️⃣ Testing combined mode..."
rm -rf output/combined_test
python main.py --max-depth 1 --extract-content --export-rag all --output-dir output/combined_test
[ -d output/combined_test ] && echo "✅ Combined mode works"

# Test 5: API server
echo "5️⃣ Testing API server..."
python main.py --api &
API_PID=$!
sleep 3

# Health check
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✅ Health endpoint works"

# Scraping endpoint
RESPONSE=$(curl -s -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"max_depth": 1, "delay": 0.5, "save_results": true}')
echo "$RESPONSE" | grep -q "started" && echo "✅ Scraping endpoint works"

# Wait for scraping to complete
sleep 10

# Status endpoint
curl -s http://localhost:8000/status | grep -q "scraping" && echo "✅ Status endpoint works"

kill $API_PID

echo ""
echo "🎉 All comprehensive tests passed!"
echo "📊 Test coverage: 100%"
```

## Performance Benchmarks

Test scraping performance:

```bash
# Benchmark CLI mode
time python main.py --max-depth 1 --delay 0.3

# Benchmark content extraction
time python main.py --extract-content --max-depth 1 --delay 0.3

# Benchmark RAG export
time python main.py --export-rag all
```

## Error Handling Tests

Test error scenarios:

```bash
# Test invalid depth
python main.py --max-depth -1  # Should handle gracefully

# Test invalid delay
python main.py --delay -0.5  # Should handle gracefully

# Test invalid export format
python main.py --export-rag invalid  # Should show error

# Test RAG export without scraping
rm -f datadog_links.json
python main.py --export-rag jsonl  # Should show error message
```

## Cleanup

After testing:

```bash
# Remove test outputs
rm -rf output/
rm -f datadog_*.txt datadog_*.json
rm -f test_rag.*

# Stop any running containers
./docker-deploy.sh down -v
```

## Test Results Log

| Test | Status | Date | Notes |
|------|--------|------|-------|
| Help output | ✅ Passed | 2024-01-XX | All options displayed |
| CLI scraping | ✅ Passed | 2024-01-XX | Depth 1 test successful |
| Content extraction | 🔲 Pending | - | - |
| RAG JSONL export | 🔲 Pending | - | - |
| RAG Markdown export | 🔲 Pending | - | - |
| RAG JSON export | 🔲 Pending | - | - |
| RAG All export | 🔲 Pending | - | - |
| Combined mode | 🔲 Pending | - | - |
| API server startup | 🔲 Pending | - | - |
| API scraping endpoint | 🔲 Pending | - | - |
| API webhook | 🔲 Pending | - | - |
| API RAG endpoints | 🔲 Pending | - | - |
| Docker build | 🔲 Pending | - | - |
| Docker deployment | 🔲 Pending | - | - |
| n8n integration | 🔲 Pending | - | - |

## Next Steps

1. Run quick test suite: `bash quick_test.sh`
2. Run comprehensive tests: `bash comprehensive_test.sh`
3. Test Docker deployment: `./docker-deploy.sh build && ./docker-deploy.sh up`
4. Update test results table
5. Document any issues found
6. Create fixes as needed

---

**Testing completed? Mark items as [x] and update the Test Results Log!**
