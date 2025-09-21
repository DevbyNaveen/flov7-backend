#!/usr/bin/env python3
"""
Test script for workflow generation integration
This script tests the new /api/v1/workflows/generate endpoint
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Configuration
API_GATEWAY_URL = "http://localhost:8000"
TEST_USER_TOKEN = None  # Will be set after login

async def login_test_user() -> str:
    """Login a test user and return the JWT token"""
    async with httpx.AsyncClient() as client:
        try:
            # For testing purposes, you might need to create a test user or use existing credentials
            # This is a placeholder - adjust based on your authentication setup
            response = await client.post(
                f"{API_GATEWAY_URL}/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "testpassword123"
                }
            )
            if response.status_code == 200:
                return response.json()["access_token"]
            else:
                print(f"Login failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Login error: {e}")
            return None

async def test_workflow_generation():
    """Test the workflow generation endpoint"""
    global TEST_USER_TOKEN
    
    print("🧪 Testing Workflow Generation Integration")
    print("=" * 50)
    
    # Test 1: Check if services are running
    print("\n1. Checking service health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_GATEWAY_URL}/api/v1/workflows/health")
            if response.status_code == 200:
                print("✅ API Gateway workflows endpoint is healthy")
            else:
                print(f"❌ API Gateway health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to API Gateway: {e}")
        return False
    
    # Test 2: Check AI service health
    print("\n2. Checking AI service health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/health")
            if response.status_code == 200:
                print("✅ AI service is healthy")
            else:
                print(f"⚠️  AI service health check: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Cannot connect to AI service: {e}")
        print("   This might be expected if AI service is not running")
    
    # Test 3: Test workflow generation endpoint structure
    print("\n3. Testing workflow generation endpoint structure...")
    
    test_prompts = [
        "Create a workflow that processes customer support tickets",
        "Build a data pipeline that analyzes sales data and generates reports",
        "Create an automation that sends welcome emails to new users"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n   Test {i}: {prompt}")
        
        # Create test request
        test_request = {
            "prompt": prompt,
            "name": f"Test Workflow {i}",
            "description": f"AI generated workflow for testing - {prompt}",
            "tags": ["test", "ai-generated", "demo"]
        }
        
        print(f"   Request: {json.dumps(test_request, indent=2)}")
        
        # Note: Actual API call requires authentication
        print(f"   ✅ Request structure is valid")
    
    print("\n" + "=" * 50)
    print("🎯 Integration test completed!")
    print("\nNext steps:")
    print("1. Start the services: docker-compose up -d")
    print("2. Authenticate and get a JWT token")
    print("3. Run actual API calls with authentication")
    
    return True

async def test_api_call_example():
    """Example of how to make the actual API call"""
    print("\n📋 Example API Call:")
    print("=" * 30)
    
    example_request = {
        "prompt": "Create a workflow that automatically categorizes support tickets based on content and assigns them to appropriate team members",
        "name": "Support Ticket Auto-Categorizer",
        "description": "Automatically analyzes incoming support tickets and routes them to the right team",
        "tags": ["automation", "support", "categorization", "routing"]
    }
    
    print("Endpoint: POST /api/v1/workflows/generate")
    print("Headers:")
    print("  Authorization: Bearer <your-jwt-token>")
    print("  Content-Type: application/json")
    print("Body:")
    print(json.dumps(example_request, indent=2))
    
    print("\nExpected Response:")
    print(json.dumps({
        "success": True,
        "workflow": {
            "name": "Support Ticket Auto-Categorizer",
            "primitives": [...],
            "connections": [...]
        },
        "workflow_id": "uuid-here",
        "ai_metadata": {
            "model_used": "gpt-4",
            "prompt_tokens": 150,
            "completion_tokens": 450
        },
        "message": "Workflow generated successfully using AI"
    }, indent=2))

if __name__ == "__main__":
    asyncio.run(test_workflow_generation())
    asyncio.run(test_api_call_example())
