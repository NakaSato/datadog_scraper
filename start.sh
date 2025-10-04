#!/bin/bash

# Datadog Scraper Startup Script
# This script helps you run the scraper in different modes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Datadog Scraper${NC}"
echo "=================="

# Function to print usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --api               Run as API server (default: CLI mode)"
    echo "  --host HOST         API server host (default: 0.0.0.0)"
    echo "  --port PORT         API server port (default: 8000)"
    echo "  --max-depth DEPTH   Maximum scraping depth (default: 2)"
    echo "  --delay SECONDS     Delay between requests (default: 0.5)"
    echo "  --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --api --port 8080                    # Run API server on port 8080"
    echo "  $0 --max-depth 3 --delay 1.0           # Run CLI with custom settings"
    echo "  $0                                     # Run CLI with defaults"
}

# Default values
MODE="cli"
HOST="0.0.0.0"
PORT="8000"
MAX_DEPTH="2"
DELAY="0.5"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --api)
            MODE="api"
            shift
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --max-depth)
            MAX_DEPTH="$2"
            shift 2
            ;;
        --delay)
            DELAY="$2"
            shift 2
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            exit 1
            ;;
    esac
done

# Check if we're in the right directory
if [[ ! -f "main.py" ]]; then
    echo -e "${RED}Error: main.py not found. Please run this script from the project root.${NC}"
    exit 1
fi

# Check if virtual environment exists and activate it
if [[ -d ".venv" ]]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Install dependencies if needed
echo -e "${YELLOW}Checking dependencies...${NC}"
python -m pip install -q -r requirements.txt || uv add -q fastapi uvicorn python-multipart

if [[ "$MODE" == "api" ]]; then
    echo -e "${GREEN}Starting API server...${NC}"
    echo -e "${BLUE}API Documentation will be available at: http://$HOST:$PORT/docs${NC}"
    echo -e "${BLUE}Health check: http://$HOST:$PORT/health${NC}"
    echo -e "${BLUE}Webhook endpoint: http://$HOST:$PORT/webhook${NC}"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
    echo ""

    python main.py --api --host "$HOST" --port "$PORT"
else
    echo -e "${GREEN}Running CLI scraper...${NC}"
    python main.py --max-depth "$MAX_DEPTH" --delay "$DELAY"
fi
