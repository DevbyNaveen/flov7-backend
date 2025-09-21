#!/bin/bash

# Workflow Generation API Test Script
# Usage: ./test_workflow_generation_curl.sh <JWT_TOKEN>

set -e

# Configuration
API_GATEWAY_URL="http://localhost:8000"
JWT_TOKEN="$1"

if [ -z "$JWT_TOKEN" ]; then
    echo "Usage: $0 <JWT_TOKEN>"
    echo ""
    echo "To get a JWT token:"
    echo "1. Login: curl -X POST $API_GATEWAY_URL/api/v1/auth/login \\"
    echo "   -H 'Content-Type: application/json' \\"
    echo "   -d '{\"email\":\"test@example.com\",\"password\":\"testpassword\"}'"
    echo ""
    exit 1
fi

echo "🚀 Testing Workflow Generation API"
echo "=================================="

# Test 1: Basic workflow generation
echo -e "\n1. Testing basic workflow generation..."
curl -X POST "$API_GATEWAY_URL/api/v1/workflows/generate" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a workflow that processes customer support tickets and assigns them to team members based on priority",
    "name": "Support Ticket Processor",
    "description": "Automatically processes and routes support tickets",
    "tags": ["support", "automation", "routing"]
  }' | python3 -m json.tool

# Test 2: Simple prompt only
echo -e "\n2. Testing simple prompt..."
curl -X POST "$API_GATEWAY_URL/api/v1/workflows/generate" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Build a data pipeline that extracts data from CSV files and sends email reports"
  }' | python3 -m json.tool

# Test 3: Error handling - empty prompt
echo -e "\n3. Testing error handling (empty prompt)..."
curl -X POST "$API_GATEWAY_URL/api/v1/workflows/generate" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": ""
  }' | python3 -m json.tool

echo -e "\n✅ All tests completed!"
echo ""
echo "Additional test examples:"
echo "- Data analysis: 'Create a workflow that analyzes sales data and generates monthly reports'"
echo "- Social media: 'Build an automation that posts content to Twitter and LinkedIn'"
echo "- E-commerce: 'Create a workflow that processes new orders and updates inventory'"
