#!/usr/bin/env python3
"""
Test script for Flov7 AI Service
Quick verification that the AI service is working correctly
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_ai_service(base_url="http://localhost:8001"):
    """Test the AI service endpoints"""
    
    print(f"🧪 Testing Flov7 AI Service at {base_url}")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   📊 Response: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Root endpoint passed")
            data = response.json()
            print(f"   📊 Service: {data.get('message')}")
            print(f"   📊 Version: {data.get('version')}")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
    
    # Test 3: Primitives endpoint
    print("\n3. Testing primitives endpoint...")
    try:
        response = requests.get(f"{base_url}/ai/primitives", timeout=5)
        if response.status_code == 200:
            print("   ✅ Primitives endpoint passed")
            data = response.json()
            print(f"   📊 Total primitives: {data.get('total_count')}")
            print(f"   📊 Primitive types: {', '.join(data.get('primitive_types', []))}")
            
            # Check each primitive has subtypes
            primitives = data.get('primitives', {})
            for ptype, pdata in primitives.items():
                subtypes_count = len(pdata.get('subtypes', {}))
                print(f"   📊 {ptype.title()}: {subtypes_count} subtypes")
        else:
            print(f"   ❌ Primitives endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Primitives endpoint error: {e}")
    
    # Test 4: Workflow validation
    print("\n4. Testing workflow validation...")
    test_workflow = {
        "name": "Test Workflow",
        "description": "A simple test workflow",
        "nodes": [
            {
                "id": "trigger_1",
                "type": "trigger",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Webhook Trigger",
                    "config": {
                        "trigger_type": "webhook",
                        "endpoint": "/webhook/test"
                    }
                }
            },
            {
                "id": "action_1",
                "type": "action",
                "position": {"x": 400, "y": 100},
                "data": {
                    "label": "Send Email",
                    "config": {
                        "action_type": "email_send",
                        "to": "test@example.com"
                    }
                }
            }
        ],
        "edges": [
            {
                "id": "edge_1",
                "source": "trigger_1",
                "target": "action_1",
                "sourceHandle": "output",
                "targetHandle": "input"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{base_url}/ai/validate", 
            json=test_workflow,
            timeout=10
        )
        if response.status_code == 200:
            print("   ✅ Workflow validation passed")
            data = response.json()
            print(f"   📊 Valid: {data.get('valid')}")
            print(f"   📊 Workflow: {data.get('workflow_name')}")
        else:
            print(f"   ❌ Workflow validation failed: {response.status_code}")
            print(f"   📊 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Workflow validation error: {e}")
    
    # Test 5: Workflow generation (only if OpenAI key is available)
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print("\n5. Testing workflow generation...")
        generation_request = {
            "prompt": "Send a welcome email when a user signs up",
            "user_id": "test_user"
        }
        
        try:
            response = requests.post(
                f"{base_url}/ai/generate",
                json=generation_request,
                timeout=30  # AI generation can take longer
            )
            if response.status_code == 200:
                print("   ✅ Workflow generation passed")
                data = response.json()
                workflow = data.get('workflow', {})
                ai_metadata = data.get('ai_metadata', {})
                
                print(f"   📊 Generated workflow: {workflow.get('name')}")
                print(f"   📊 Description: {workflow.get('description')}")
                print(f"   📊 Nodes: {len(workflow.get('nodes', []))}")
                print(f"   📊 Edges: {len(workflow.get('edges', []))}")
                
                if ai_metadata.get('usage'):
                    usage = ai_metadata['usage']
                    print(f"   📊 AI Usage - Total tokens: {usage.get('total_tokens')}")
                    print(f"   📊 AI Model: {ai_metadata.get('model')}")
                
            elif response.status_code == 429:
                print("   ⚠️  Rate limited - too many requests")
            else:
                print(f"   ❌ Workflow generation failed: {response.status_code}")
                print(f"   📊 Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Workflow generation error: {e}")
    else:
        print("\n5. Skipping workflow generation test (no OpenAI API key)")
    
    print("\n" + "=" * 50)
    print("🎉 AI Service testing completed!")
    print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Flov7 AI Service')
    parser.add_argument(
        '--url', 
        default='http://localhost:8001',
        help='Base URL of the AI service (default: http://localhost:8001)'
    )
    
    args = parser.parse_args()
    
    try:
        test_ai_service(args.url)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
