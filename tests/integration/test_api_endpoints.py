"""
Integration tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

# Import the FastAPI app instances for each service
# Note: These import paths may need adjustment based on actual project structure
from app.main import app as api_gateway_app

# Import individual service apps for testing
import sys
import os

# Add service directories to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'ai-service'))
sys.path.insert(0, os.path.join(project_root, 'workflow-service'))

try:
    from ai_service.app.main import app as ai_service_app
except ImportError:
    ai_service_app = None

try:
    from workflow_service.app.main import app as workflow_service_app
except ImportError:
    workflow_service_app = None


class TestAPIGatewayEndpoints:
    """Integration tests for API Gateway endpoints"""
    
    def setup_method(self):
        """Setup test method"""
        self.client = TestClient(api_gateway_app)
    
    def test_root_endpoint(self):
        """Test API Gateway root endpoint"""
        response = self.client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert "Flov7" in response.json()["message"]
    
    def test_health_endpoint(self):
        """Test API Gateway health endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.skipif(ai_service_app is None, reason="AI Service app not available")
class TestAIServiceEndpoints:
    """Integration tests for AI Service endpoints"""
    
    def setup_method(self):
        """Setup test method"""
        self.client = TestClient(ai_service_app)
    
    def test_ai_root_endpoint(self):
        """Test AI Service root endpoint"""
        response = self.client.get("/ai/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["message"] == "Flov7 AI Service"
    
    def test_ai_health_endpoint(self):
        """Test AI Service health endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_get_primitives_endpoint(self):
        """Test get primitives endpoint"""
        response = self.client.get("/primitives")
        assert response.status_code == 200
        primitives = response.json()
        assert len(primitives) == 5


@pytest.mark.skipif(workflow_service_app is None, reason="Workflow Service app not available")
class TestWorkflowServiceEndpoints:
    """Integration tests for Workflow Service endpoints"""
    
    def setup_method(self):
        """Setup test method"""
        self.client = TestClient(workflow_service_app)
    
    def test_workflow_root_endpoint(self):
        """Test Workflow Service root endpoint"""
        response = self.client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["message"] == "Flov7 Workflow Service"
    
    def test_workflow_health_endpoint(self):
        """Test Workflow Service health endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__])
