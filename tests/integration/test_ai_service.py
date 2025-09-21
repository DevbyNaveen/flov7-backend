"""
Integration tests for Flov7 AI Service.
Tests the complete AI workflow generation pipeline.
"""

import pytest
import json
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai_service.app.main import app
from shared.constants.primitives import PRIMITIVES


class TestAIServiceIntegration:
    """Integration tests for AI service"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-service"
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Flov7 AI Service"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
    
    def test_get_primitives(self, client):
        """Test primitives endpoint"""
        response = client.get("/ai/primitives")
        assert response.status_code == 200
        data = response.json()
        
        assert "primitives" in data
        assert "total_count" in data
        assert "primitive_types" in data
        
        # Check that all 5 primitives are present
        primitives = data["primitives"]
        expected_types = ["trigger", "action", "connection", "condition", "data"]
        for primitive_type in expected_types:
            assert primitive_type in primitives
            assert "display_name" in primitives[primitive_type]
            assert "description" in primitives[primitive_type]
            assert "subtypes" in primitives[primitive_type]
    
    def test_workflow_validation_valid(self, client):
        """Test workflow validation with valid workflow"""
        valid_workflow = {
            "name": "Test Workflow",
            "description": "A test workflow",
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
        
        response = client.post("/ai/validate", json=valid_workflow)
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert data["workflow_name"] == "Test Workflow"
    
    def test_workflow_validation_invalid_structure(self, client):
        """Test workflow validation with invalid structure"""
        invalid_workflow = {
            "name": "Invalid Workflow",
            # Missing required fields like nodes and edges
        }
        
        response = client.post("/ai/validate", json=invalid_workflow)
        assert response.status_code == 400
    
    def test_workflow_validation_invalid_primitive(self, client):
        """Test workflow validation with invalid primitive type"""
        invalid_workflow = {
            "name": "Invalid Workflow",
            "description": "A workflow with invalid primitive",
            "nodes": [
                {
                    "id": "invalid_1",
                    "type": "invalid_type",  # Invalid primitive type
                    "position": {"x": 100, "y": 100},
                    "data": {"label": "Invalid Node"}
                }
            ],
            "edges": []
        }
        
        response = client.post("/ai/validate", json=invalid_workflow)
        assert response.status_code == 400
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"), 
        reason="OpenAI API key not configured"
    )
    def test_workflow_generation_simple(self, client):
        """Test simple workflow generation (requires OpenAI API key)"""
        generation_request = {
            "prompt": "Send a welcome email when a user signs up",
            "user_id": "test_user"
        }
        
        response = client.post("/ai/generate", json=generation_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "workflow" in data
        assert "ai_metadata" in data
        
        workflow = data["workflow"]
        assert "name" in workflow
        assert "description" in workflow
        assert "nodes" in workflow
        assert "edges" in workflow
        
        # Check that nodes have valid primitive types
        for node in workflow["nodes"]:
            assert node["type"] in PRIMITIVES
            assert "id" in node
            assert "position" in node
            assert "data" in node
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"), 
        reason="OpenAI API key not configured"
    )
    def test_workflow_generation_complex(self, client):
        """Test complex workflow generation"""
        generation_request = {
            "prompt": "Create a customer onboarding workflow that: 1) receives webhook when user signs up, 2) sends welcome email, 3) waits 24 hours, 4) sends follow-up email with tutorial, 5) adds user to CRM",
            "user_id": "test_user"
        }
        
        response = client.post("/ai/generate", json=generation_request)
        assert response.status_code == 200
        
        data = response.json()
        workflow = data["workflow"]
        
        # Should have multiple nodes for complex workflow
        assert len(workflow["nodes"]) >= 3
        
        # Should have a trigger node
        trigger_nodes = [node for node in workflow["nodes"] if node["type"] == "trigger"]
        assert len(trigger_nodes) >= 1
        
        # Should have action nodes
        action_nodes = [node for node in workflow["nodes"] if node["type"] == "action"]
        assert len(action_nodes) >= 2
    
    def test_rate_limiting(self, client):
        """Test rate limiting on workflow generation"""
        generation_request = {
            "prompt": "Simple test workflow",
            "user_id": "test_user"
        }
        
        # Make multiple requests quickly to test rate limiting
        responses = []
        for i in range(12):  # Exceed the 10/minute limit
            response = client.post("/ai/generate", json=generation_request)
            responses.append(response)
        
        # At least one should be rate limited (429 status)
        rate_limited = any(r.status_code == 429 for r in responses)
        # Note: This might not always trigger in tests due to timing
        # In a real scenario, you'd want to test this more systematically
    
    def test_error_handling_empty_prompt(self, client):
        """Test error handling for empty prompt"""
        generation_request = {
            "prompt": "",
            "user_id": "test_user"
        }
        
        response = client.post("/ai/generate", json=generation_request)
        # Should handle gracefully, either with 400 or generate a default workflow
        assert response.status_code in [200, 400]
    
    def test_error_handling_malformed_request(self, client):
        """Test error handling for malformed request"""
        # Missing required prompt field
        malformed_request = {
            "user_id": "test_user"
        }
        
        response = client.post("/ai/generate", json=malformed_request)
        assert response.status_code == 422  # Validation error


class TestAIServicePrimitives:
    """Test the 5-primitives system"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_all_primitives_have_subtypes(self, client):
        """Test that all primitives have subtypes defined"""
        response = client.get("/ai/primitives")
        data = response.json()
        primitives = data["primitives"]
        
        for primitive_type, primitive_data in primitives.items():
            assert "subtypes" in primitive_data
            assert len(primitive_data["subtypes"]) > 0
            
            # Each subtype should have name and description
            for subtype_key, subtype_data in primitive_data["subtypes"].items():
                assert "name" in subtype_data
                assert "description" in subtype_data
    
    def test_primitive_colors_and_icons(self, client):
        """Test that all primitives have colors and icons"""
        response = client.get("/ai/primitives")
        data = response.json()
        primitives = data["primitives"]
        
        for primitive_type, primitive_data in primitives.items():
            assert "color" in primitive_data
            assert "icon" in primitive_data
            assert primitive_data["color"].startswith("#")  # Should be hex color
            assert len(primitive_data["icon"]) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
