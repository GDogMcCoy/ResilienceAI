#!/bin/bash
# ResilienceAI - Archia Cloud Deployment Script
# Usage: ./deploy-to-archia.sh

set -e

echo "🚀 ResilienceAI Archia Cloud Deployment"
echo "========================================"

# Configuration
ARCHIA_API_KEY="ask_ouIAvAYrMqb8LnlJxfDeU3hvOdEkOpA3EGmiS0XlWvc="
ARCHIA_WORKSPACE="resilienceai-hackathon"
ARCHIA_ENDPOINT="https://api.archia.app/v1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"
if ! command -v curl &> /dev/null; then
    echo -e "${RED}curl is required but not installed.${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}python3 is required but not installed.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Dependencies OK${NC}"

# Verify data exists
echo -e "${YELLOW}Verifying data files...${NC}"
if [ ! -f "data/processed/county_features.csv" ]; then
    echo -e "${RED}County features data not found. Run pipeline first:${NC}"
    echo "  python run_pipeline.py"
    exit 1
fi

echo -e "${GREEN}✓ Data files OK${NC}"

# Test Archia API connection
echo -e "${YELLOW}Testing Archia API connection...${NC}"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer ${ARCHIA_API_KEY}" \
    -H "Content-Type: application/json" \
    "${ARCHIA_ENDPOINT}/health" 2>/dev/null || echo "000")

if [ "$HTTP_STATUS" != "200" ]; then
    echo -e "${RED}Cannot connect to Archia API (HTTP ${HTTP_STATUS})${NC}"
    echo "Please check your API key and network connection."
    exit 1
fi

echo -e "${GREEN}✓ Archia API connection OK${NC}"

# Deploy agent configuration
echo -e "${YELLOW}Deploying ResilienceAI agent to Archia...${NC}"

# Create agent payload
python3 << EOF
import json
import base64

# Read archia.toml
with open('archia/archia.toml', 'r') as f:
    config = f.read()

# Create deployment payload
payload = {
    "name": "resilienceai",
    "display_name": "ResilienceAI - Disaster Vulnerability Agent",
    "description": "Disaster Vulnerability & Health Infrastructure Gap Assessment Agent with 23 MCP tools",
    "config": config,
    "version": "1.0.0",
    "tags": ["hackathon", "muidsi-2026", "disaster-preparedness", "health-infrastructure"],
    "environment_variables": {
        "DATA_PATH": "/data/county_features.csv",
        "MODELS_DIR": "/data/models"
    }
}

# Save payload
with open('/tmp/archia_deploy_payload.json', 'w') as f:
    json.dump(payload, f, indent=2)

print("✓ Deployment payload created")
EOF

# Deploy to Archia
echo -e "${YELLOW}Uploading to Archia Cloud...${NC}"
DEPLOY_RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Authorization: Bearer ${ARCHIA_API_KEY}" \
    -H "Content-Type: application/json" \
    -d @/tmp/archia_deploy_payload.json \
    "${ARCHIA_ENDPOINT}/agents/deploy" 2>/dev/null)

HTTP_CODE=$(echo "$DEPLOY_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$DEPLOY_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "201" ]; then
    echo -e "${GREEN}✓ Agent deployed successfully!${NC}"
    echo ""
    echo "Deployment Details:"
    echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo -e "${RED}✗ Deployment failed (HTTP ${HTTP_CODE})${NC}"
    echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
    exit 1
fi

# Test the deployed agent
echo ""
echo -e "${YELLOW}Testing deployed agent...${NC}"

TEST_RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Authorization: Bearer ${ARCHIA_API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "Which Missouri counties are most vulnerable?",
        "max_tokens": 500
    }' \
    "${ARCHIA_ENDPOINT}/agents/resilienceai/query" 2>/dev/null)

HTTP_CODE=$(echo "$TEST_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$TEST_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✓ Agent test successful!${NC}"
    echo ""
    echo "Sample Response:"
    echo "$RESPONSE_BODY" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('response', 'No response')[:200] + '...')" 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo -e "${YELLOW}⚠ Agent test returned HTTP ${HTTP_CODE}${NC}"
    echo "The agent is deployed but may need a moment to initialize."
fi

# Print summary
echo ""
echo "========================================"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "========================================"
echo ""
echo "Your ResilienceAI agent is now running on Archia Cloud."
echo ""
echo "Next Steps:"
echo "  1. Open the dashboard: streamlit run app/dashboard.py"
echo "  2. Navigate to the 'Agent Query' tab"
echo "  3. Enter the Archia endpoint in the sidebar:"
echo "     ${ARCHIA_ENDPOINT}"
echo "  4. Start asking questions!"
echo ""
echo "Example queries:"
echo "  • 'Which Missouri counties are most vulnerable to flooding?'"
echo "  • 'Show me compound risk hotspots'"
echo "  • 'Which counties have zero hospital redundancy?'"
echo ""
echo "Dashboard URL: http://localhost:8501"
echo ""
