#!/bin/bash

# AI Service to Workflow Service Integration Test Script
# This script tests the complete integration between AI Service and Workflow Service

echo "🚀 Testing AI Service to Workflow Service Integration"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Service URLs
AI_SERVICE_URL="http://localhost:8001"
WORKFLOW_SERVICE_URL="http://localhost:8002"

# Test user ID
TEST_USER_ID="test-user-$(date +%s)"

# Function to check if services are running
check_services() {
    echo "🔍 Checking if services are running..."
    
    # Check AI Service
    if curl -s "$AI_SERVICE_URL/health" > /dev/null; then
        echo -e "${GREEN}✅ AI Service is running${NC}"
    else
        echo -e "${RED}❌ AI Service is not running${NC}"
        exit 1
    fi
    
    # Check Workflow Service
    if curl -s "$WORKFLOW_SERVICE_URL/health" > /dev/null; then
        echo -e "${GREEN}✅ Workflow Service is running${NC}"
    else
        echo -e "${RED}❌ Workflow Service is not running${NC}"
        exit 1
    fi
}

# Function to test workflow generation
test_workflow_generation() {
    echo ""
    echo "📝 Testing workflow generation..."
    
    response=$(curl -s -X POST "$AI_SERVICE_URL/ai/generate" \
        -H "Content-Type: application/json" \
        -d '{
            "prompt": "Create a workflow that processes customer support tickets automatically",
            "user_id": "'$TEST_USER_ID'"
        }')
    
    if echo "$response" | jq -e '.workflow' > /dev/null; then
        echo -e "${GREEN}✅ Workflow generated successfully${NC}"
        WORKFLOW_ID=$(echo "$response" | jq -r '.ai_metadata.workflow_id')
        echo "📋 Workflow ID: $WORKFLOW_ID"
        
        # Save the response for later use
        echo "$response" > /tmp/generated_workflow.json
    else
        echo -e "${RED}❌ Workflow generation failed${NC}"
        echo "Response: $response"
        exit 1
    fi
}

# Function to test workflow execution
test_workflow_execution() {
    echo ""
    echo "⚡ Testing workflow execution..."
    
    if [ -z "$WORKFLOW_ID" ]; then
        echo -e "${RED}❌ No workflow ID available${NC}"
        exit 1
    fi
    
    response=$(curl -s -X POST "$AI_SERVICE_URL/ai/workflows/$WORKFLOW_ID/execute" \
        -H "Content-Type: application/json" \
        -d '{
            "user_id": "'$TEST_USER_ID'"
        }')
    
    if echo "$response" | jq -e '.execution_id' > /dev/null; then
        echo -e "${GREEN}✅ Workflow execution started successfully${NC}"
        EXECUTION_ID=$(echo "$response" | jq -r '.execution_id')
        echo "🎯 Execution ID: $EXECUTION_ID"
        
        # Save the response
        echo "$response" > /tmp/workflow_execution.json
    else
        echo -e "${RED}❌ Workflow execution failed${NC}"
        echo "Response: $response"
        exit 1
    fi
}

# Function to test execution status
test_execution_status() {
    echo ""
    echo "📊 Testing execution status..."
    
    if [ -z "$EXECUTION_ID" ]; then
        echo -e "${RED}❌ No execution ID available${NC}"
        exit 1
    fi
    
    response=$(curl -s "$AI_SERVICE_URL/ai/workflows/execution/$EXECUTION_ID/status?user_id=$TEST_USER_ID")
    
    if echo "$response" | jq -e '.status' > /dev/null; then
        echo -e "${GREEN}✅ Execution status retrieved successfully${NC}"
        STATUS=$(echo "$response" | jq -r '.status')
        echo "📈 Current status: $STATUS"
    else
        echo -e "${RED}❌ Failed to get execution status${NC}"
        echo "Response: $response"
        exit 1
    fi
}

# Function to test generate-and-execute
test_generate_and_execute() {
    echo ""
    echo "🔄 Testing generate-and-execute workflow..."
    
    response=$(curl -s -X POST "$AI_SERVICE_URL/ai/workflows/generate-and-execute" \
        -H "Content-Type: application/json" \
        -d '{
            "prompt": "Create a simple workflow that sends a welcome email to new users",
            "user_id": "'$TEST_USER_ID'"
        }')
    
    if echo "$response" | jq -e '.workflow and .execution' > /dev/null; then
        echo -e "${GREEN}✅ Generate-and-execute workflow completed successfully${NC}"
        GEN_EXEC_WORKFLOW_ID=$(echo "$response" | jq -r '.ai_metadata.workflow_id')
        GEN_EXEC_EXECUTION_ID=$(echo "$response" | jq -r '.execution.execution_id')
        echo "📋 Generated workflow ID: $GEN_EXEC_WORKFLOW_ID"
        echo "🎯 Execution ID: $GEN_EXEC_EXECUTION_ID"
    else
        echo -e "${RED}❌ Generate-and-execute workflow failed${NC}"
        echo "Response: $response"
        exit 1
    fi
}

# Function to test direct workflow service execution
test_direct_workflow_service() {
    echo ""
    echo "🎯 Testing direct Workflow Service execution..."
    
    # Use the generated workflow from earlier
    if [ -f /tmp/generated_workflow.json ]; then
        workflow_data=$(cat /tmp/generated_workflow.json | jq '.workflow')
        
        response=$(curl -s -X POST "$WORKFLOW_SERVICE_URL/workflow/execute" \
            -H "Content-Type: application/json" \
            -d '{
                "workflow_data": '$workflow_data',
                "user_id": "'$TEST_USER_ID'"
            }')
        
        if echo "$response" | jq -e '.execution_id' > /dev/null; then
            echo -e "${GREEN}✅ Direct Workflow Service execution successful${NC}"
            DIRECT_EXECUTION_ID=$(echo "$response" | jq -r '.execution_id')
            echo "🎯 Direct execution ID: $DIRECT_EXECUTION_ID"
        else
            echo -e "${RED}❌ Direct Workflow Service execution failed${NC}"
            echo "Response: $response"
        fi
    fi
}

# Function to display usage examples
show_usage_examples() {
    echo ""
    echo "📚 Usage Examples"
    echo "================="
    echo ""
    echo "1. Generate a workflow:"
    echo "   curl -X POST $AI_SERVICE_URL/ai/generate \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -d '{\"prompt\": \"Create a workflow...\", \"user_id\": \"user123\"}'"
    echo ""
    echo "2. Execute a workflow:"
    echo "   curl -X POST $AI_SERVICE_URL/ai/workflows/{workflow_id}/execute \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -d '{\"user_id\": \"user123\"}'"
    echo ""
    echo "3. Check execution status:"
    echo "   curl \"$AI_SERVICE_URL/ai/workflows/execution/{execution_id}/status?user_id=user123\""
    echo ""
    echo "4. Generate and execute in one call:"
    echo "   curl -X POST $AI_SERVICE_URL/ai/workflows/generate-and-execute \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -d '{\"prompt\": \"Create a workflow...\", \"user_id\": \"user123\"}'"
    echo ""
}

# Main execution
main() {
    check_services
    test_workflow_generation
    test_workflow_execution
    test_execution_status
    test_generate_and_execute
    test_direct_workflow_service
    
    echo ""
    echo -e "${GREEN}🎉 All integration tests completed successfully!${NC}"
    echo ""
    show_usage_examples
}

# Run main function
main "$@"
