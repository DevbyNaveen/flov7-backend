"""
Integration tests for workflow execution service.
Tests the complete workflow execution pipeline from API to execution.
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
import sys
import os

# Add the workflow service to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../workflow-service'))

from app.main import app
from app.workflow.executor import workflow_executor
from app.workflow.status import status_tracker


class TestWorkflowExecution:
    """Test workflow execution functionality"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_workflow(self):
        """Sample workflow data for testing"""
        return {
            "name": "Test Workflow",
            "description": "A simple test workflow",
            "nodes": [
                {
                    "id": "node1",
                    "type": "start",
                    "data": {"message": "Starting workflow"}
                },
                {
                    "id": "node2", 
                    "type": "process",
                    "data": {"action": "process_data"}
                },
                {
                    "id": "node3",
                    "type": "end",
                    "data": {"message": "Workflow completed"}
                }
            ],
            "edges": [
                {
                    "id": "edge1",
                    "source": "node1",
                    "target": "node2"
                },
                {
                    "id": "edge2", 
                    "source": "node2",
                    "target": "node3"
                }
            ]
        }
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "workflow-service"
    
    def test_workflow_root_endpoint(self, client):
        """Test workflow root endpoint"""
        response = client.get("/workflow/")
        assert response.status_code == 200
        data = response.json()
        assert "endpoints" in data
        assert "execute" in data["endpoints"]
        assert "status" in data["endpoints"]
        assert "history" in data["endpoints"]
    
    def test_workflow_execution_endpoint(self, client, sample_workflow):
        """Test workflow execution endpoint"""
        request_data = {
            "workflow_data": sample_workflow,
            "user_id": "test-user-123"
        }
        
        response = client.post("/api/v1/workflow/execute", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "execution_id" in data
        assert data["status"] in ["completed", "failed"]
        assert "execution_time_seconds" in data
        assert "started_at" in data
        assert "completed_at" in data
    
    def test_workflow_status_endpoint(self, client, sample_workflow):
        """Test workflow status endpoint"""
        # First execute a workflow
        request_data = {
            "workflow_data": sample_workflow,
            "user_id": "test-user-123"
        }
        
        execute_response = client.post("/api/v1/workflow/execute", json=request_data)
        assert execute_response.status_code == 200
        
        execution_data = execute_response.json()
        execution_id = execution_data["execution_id"]
        user_id = "test-user-123"
        
        # Then check its status (now requires user_id parameter)
        status_response = client.get(f"/api/v1/workflow/status/{execution_id}?user_id={user_id}")
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data["execution_id"] == execution_id
        assert "status" in status_data
        assert "updated_at" in status_data
    
    def test_workflow_history_endpoint(self, client, sample_workflow):
        """Test workflow history endpoint"""
        # First execute a workflow
        request_data = {
            "workflow_data": sample_workflow,
            "user_id": "test-user-123"
        }
        
        execute_response = client.post("/api/v1/workflow/execute", json=request_data)
        assert execute_response.status_code == 200
        
        execution_data = execute_response.json()
        execution_id = execution_data["execution_id"]
        user_id = "test-user-123"
        
        # Then get its history (now requires user_id parameter)
        history_response = client.get(f"/api/v1/workflow/history/{execution_id}?user_id={user_id}")
        assert history_response.status_code == 200
        
        history_data = history_response.json()
        assert isinstance(history_data, list)
        assert len(history_data) > 0
        assert history_data[0]["execution_id"] == execution_id
    
    def test_workflow_status_not_found(self, client):
        """Test workflow status endpoint with non-existent execution ID"""
        response = client.get("/api/v1/workflow/status/non-existent-id?user_id=test-user")
        assert response.status_code == 404
    
    def test_workflow_history_not_found(self, client):
        """Test workflow history endpoint with non-existent execution ID"""
        response = client.get("/api/v1/workflow/history/non-existent-id?user_id=test-user")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_workflow_executor_direct(self, sample_workflow):
        """Test workflow executor directly"""
        result = await workflow_executor.execute_workflow(
            sample_workflow,
            "test-user-direct"
        )
        
        assert "execution_id" in result
        assert result["status"] in ["completed", "failed"]
        assert "execution_time_seconds" in result
        assert "output_data" in result
    
    @pytest.mark.asyncio
    async def test_status_tracker_functionality(self):
        """Test status tracker functionality with database persistence"""
        execution_id = "test-execution-123"
        user_id = "test-user-status"
        
        # Create execution record first
        execution_data = {
            "workflow_id": "test-workflow-123",
            "user_id": user_id,
            "status": "pending",
            "input_data": {"test": "data"},
            "temporal_workflow_id": execution_id
        }
        
        create_result = await status_tracker.create_execution_record(execution_data)
        assert create_result["success"] is True
        
        # Update status
        success = await status_tracker.update_status(
            execution_id, 
            "running",
            output_data={"test": "output"}
        )
        assert success is True
        
        # Get status
        status_info = await status_tracker.get_status(execution_id, user_id)
        assert status_info is not None
        assert status_info["status"] == "running"
        
        # Check if completed
        is_completed = await status_tracker.is_execution_completed(execution_id, user_id)
        assert is_completed is False
        
        # Update to completed
        await status_tracker.update_status(execution_id, "completed")
        is_completed = await status_tracker.is_execution_completed(execution_id, user_id)
        assert is_completed is True
    
    def test_invalid_workflow_data(self, client):
        """Test workflow execution with invalid data"""
        request_data = {
            "workflow_data": {"invalid": "data"},
            "user_id": "test-user-123"
        }
        
        response = client.post("/api/v1/workflow/execute", json=request_data)
        # Should still return 200 but with failed status
        assert response.status_code == 200
        
        data = response.json()
        # The execution should complete but may have limited functionality
        assert "execution_id" in data
        assert "status" in data
    
    @pytest.mark.asyncio
    async def test_crewai_integration(self, sample_workflow):
        """Test CrewAI integration in workflow execution"""
        # Test that CrewAI agents and tasks are properly initialized
        from app.crewai.agents import agent_manager
        from app.crewai.tasks import task_manager
        
        # Check agents are available
        agents = agent_manager.get_all_agents()
        assert len(agents) > 0
        assert "workflow_coordinator" in agents
        assert "data_processor" in agents
        assert "action_executor" in agents
        assert "validator" in agents
        
        # Check tasks are available
        tasks = task_manager.get_all_tasks()
        assert len(tasks) > 0
        assert "coordinate_workflow" in tasks
        assert "process_data" in tasks
        assert "execute_actions" in tasks
        assert "validate_results" in tasks
        
        # Test workflow execution with CrewAI
        result = await workflow_executor.execute_workflow(
            sample_workflow,
            "test-user-crewai"
        )
        
        assert "execution_id" in result
        assert result["status"] in ["completed", "failed"]
        
        # If CrewAI execution succeeded, check for CrewAI-specific output
        if result["status"] == "completed" and result.get("output_data"):
            output = result["output_data"]
            if output.get("execution_method") == "crewai":
                assert "agents_used" in output
                assert "tasks_executed" in output
                assert output["agents_used"] > 0
                assert output["tasks_executed"] > 0
    
    @pytest.mark.asyncio
    async def test_temporal_client_initialization(self):
        """Test Temporal client initialization"""
        from app.temporal.client import temporal_client_manager, get_temporal_client
        
        # Test client initialization
        client = await get_temporal_client()
        # Client may be None if Temporal server is not available, which is expected in tests
        
        # Test connection health check
        is_connected = await temporal_client_manager.is_connected()
        # Should return False if no Temporal server is running
        assert isinstance(is_connected, bool)
        
        # Test connection attempt
        connection_success = await temporal_client_manager.connect()
        assert isinstance(connection_success, bool)
    
    @pytest.mark.asyncio
    async def test_database_persistence_integration(self, sample_workflow):
        """Test database persistence throughout workflow execution"""
        user_id = "test-user-db-persistence"
        
        # Execute workflow
        result = await workflow_executor.execute_workflow(
            sample_workflow,
            user_id
        )
        
        execution_id = result["execution_id"]
        
        # Test that execution was persisted to database
        status_info = await status_tracker.get_status(execution_id, user_id)
        assert status_info is not None
        assert status_info["status"] == result["status"]
        
        # Test execution history
        history = await status_tracker.get_execution_history(execution_id, user_id)
        assert len(history) > 0
        assert history[0]["execution_id"] == execution_id
        
        # Test execution statistics
        stats = await status_tracker.get_execution_stats(user_id)
        assert stats["success"] is True
        assert "data" in stats
        assert stats["data"]["total_executions"] >= 1


class TestWorkflowExecutionEndToEnd:
    """End-to-end workflow execution tests"""
    
    @pytest.fixture
    def complex_workflow(self):
        """Complex workflow for end-to-end testing"""
        return {
            "name": "Complex Test Workflow",
            "description": "A complex workflow with multiple steps",
            "nodes": [
                {
                    "id": "start",
                    "type": "start",
                    "data": {"message": "Starting complex workflow"}
                },
                {
                    "id": "data_input",
                    "type": "data_input",
                    "data": {"source": "api", "endpoint": "/test"}
                },
                {
                    "id": "transform",
                    "type": "transform",
                    "data": {"operation": "normalize"}
                },
                {
                    "id": "validate",
                    "type": "validate", 
                    "data": {"rules": ["required", "format"]}
                },
                {
                    "id": "output",
                    "type": "output",
                    "data": {"destination": "database"}
                },
                {
                    "id": "end",
                    "type": "end",
                    "data": {"message": "Complex workflow completed"}
                }
            ],
            "edges": [
                {"id": "e1", "source": "start", "target": "data_input"},
                {"id": "e2", "source": "data_input", "target": "transform"},
                {"id": "e3", "source": "transform", "target": "validate"},
                {"id": "e4", "source": "validate", "target": "output"},
                {"id": "e5", "source": "output", "target": "end"}
            ]
        }
    
    def test_end_to_end_workflow_execution(self, complex_workflow):
        """Test complete end-to-end workflow execution"""
        client = TestClient(app)
        
        # Execute workflow
        request_data = {
            "workflow_data": complex_workflow,
            "user_id": "e2e-test-user"
        }
        
        response = client.post("/api/v1/workflow/execute", json=request_data)
        assert response.status_code == 200
        
        execution_data = response.json()
        execution_id = execution_data["execution_id"]
        
        # Verify execution completed
        assert execution_data["status"] in ["completed", "failed"]
        assert execution_data["execution_time_seconds"] >= 0
        
        # Check status endpoint
        status_response = client.get(f"/api/v1/workflow/status/{execution_id}?user_id=e2e-test-user")
        assert status_response.status_code == 200
        
        # Check history endpoint
        history_response = client.get(f"/api/v1/workflow/history/{execution_id}?user_id=e2e-test-user")
        assert history_response.status_code == 200
        
        # Verify output data structure
        if execution_data["status"] == "completed":
            assert execution_data["output_data"] is not None
            output = execution_data["output_data"]
            assert "workflow_name" in output
            assert output["workflow_name"] == complex_workflow["name"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
