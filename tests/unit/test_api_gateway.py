"""
Basic test to verify API Gateway service can start and respond to health check.
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add all service app directories to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api-gateway', 'app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-service', 'app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'workflow-service', 'app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api-gateway'))

try:
    from app.main import app
except ImportError:
    pytest.skip("API Gateway app not available for testing", allow_module_level=True)

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns correct response."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Flov7 API Gateway" in data["message"]
    assert "version" in data
    assert "status" in data

def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "api-gateway"

def test_api_v1_endpoint():
    """Test the API v1 root endpoint."""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "Flov7 API Gateway v1" in data["message"]
    assert "endpoints" in data
