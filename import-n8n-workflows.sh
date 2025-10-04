#!/bin/bash

# n8n Workflow Import Script
# This script helps you import the provided workflow templates into n8n

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print usage
usage() {
    echo "Usage: $0 [WORKFLOW_NAME]"
    echo ""
    echo "Available workflows:"
    echo "  basic-trigger       Basic webhook-triggered scraping"
    echo "  scheduled          Scheduled scraping (weekly)"
    echo "  results-processor  Process results and send notifications"
    echo "  complete-automation Full automation with notifications"
    echo "  docker-integration Docker-optimized workflow"
    echo "  list               List all available workflows"
    echo "  import-all         Import all workflows"
    echo "  help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 basic-trigger              # Import basic trigger workflow"
    echo "  $0 import-all                 # Import all workflows"
    echo "  $0 list                       # Show workflow descriptions"
}

# List available workflows
list_workflows() {
    echo -e "${BLUE}n8n Workflow Templates${NC}"
    echo "======================"
    echo ""
    echo -e "${GREEN}1. Basic Trigger Workflow${NC}"
    echo "   File: basic-trigger-workflow.json"
    echo "   Description: Simple webhook-triggered scraping"
    echo "   Use case: Manual triggering via webhooks"
    echo ""
    echo -e "${GREEN}2. Scheduled Scraping Workflow${NC}"
    echo "   File: scheduled-scraping-workflow.json"
    echo "   Description: Automated weekly scraping"
    echo "   Use case: Regular documentation monitoring"
    echo ""
    echo -e "${GREEN}3. Results Processing Workflow${NC}"
    echo "   File: results-processing-workflow.json"
    echo "   Description: Process results and send notifications"
    echo "   Use case: Result analysis and alerting"
    echo ""
    echo -e "${GREEN}4. Complete Automation Workflow${NC}"
    echo "   File: complete-automation-workflow.json"
    echo "   Description: Full end-to-end automation"
    echo "   Use case: Production scraping with notifications"
    echo ""
    echo -e "${GREEN}5. Docker Integration Workflow${NC}"
    echo "   File: docker-integration-workflow.json"
    echo "   Description: Optimized for Docker deployment"
    echo "   Use case: Containerized scraping workflows"
    echo ""
    echo -e "${YELLOW}Import Steps:${NC}"
    echo "1. Open n8n in your browser"
    echo "2. Go to the workflow canvas"
    echo "3. Click menu (≡) → 'Import from File'"
    echo "4. Select the workflow JSON file"
    echo "5. Configure environment variables"
    echo "6. Test and activate the workflow"
}

# Import a specific workflow
import_workflow() {
    local workflow_name="$1"
    local file_path="n8n-workflows/${workflow_name}-workflow.json"

    if [[ ! -f "$file_path" ]]; then
        echo -e "${RED}Error: Workflow file '$file_path' not found.${NC}"
        echo ""
        echo -e "${YELLOW}Available workflows:${NC}"
        for file in n8n-workflows/*-workflow.json; do
            if [[ -f "$file" ]]; then
                filename=$(basename "$file" .json)
                echo "  - ${filename%-workflow}"
            fi
        done
        exit 1
    fi

    echo -e "${BLUE}Importing workflow: $workflow_name${NC}"
    echo -e "${YELLOW}File: $file_path${NC}"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Open n8n in your browser"
    echo "2. Go to the workflow canvas"
    echo "3. Click menu (≡) → 'Import from File'"
    echo "4. Select: $file_path"
    echo "5. Update SCRAPER_URL to: http://localhost:8000 (or your scraper URL)"
    echo "6. Configure any notification webhooks"
    echo "7. Test the workflow"
    echo ""
    echo -e "${BLUE}Press Enter to open file location...${NC}"
    read -r
    echo -e "${YELLOW}Opening workflow file...${NC}"
    if command -v open &> /dev/null; then
        open "$file_path"
    elif command -v xdg-open &> /dev/null; then
        xdg-open "$file_path"
    else
        echo -e "${YELLOW}File location: $(pwd)/$file_path${NC}"
    fi
}

# Import all workflows
import_all_workflows() {
    echo -e "${BLUE}Importing all workflows...${NC}"
    echo ""

    for file in n8n-workflows/*-workflow.json; do
        if [[ -f "$file" ]]; then
            filename=$(basename "$file" .json)
            workflow_name="${filename%-workflow}"
            echo -e "${GREEN}✓${NC} $workflow_name"
        fi
    done

    echo ""
    echo -e "${YELLOW}To import all workflows:${NC}"
    echo "1. Use the individual import commands above"
    echo "2. Or manually import each file in n8n"
    echo ""
    echo -e "${BLUE}Workflow files are ready in: $(pwd)/n8n-workflows/${NC}"
}

# Main logic
case "${1:-list}" in
    basic-trigger|basic)
        import_workflow "basic-trigger"
        ;;
    scheduled)
        import_workflow "scheduled-scraping"
        ;;
    results-processor|results)
        import_workflow "results-processing"
        ;;
    complete-automation|complete|automation)
        import_workflow "complete-automation"
        ;;
    docker-integration|docker)
        import_workflow "docker-integration"
        ;;
    list)
        list_workflows
        ;;
    import-all)
        import_all_workflows
        ;;
    help|*)
        usage
        ;;
esac
