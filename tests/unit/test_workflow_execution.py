"""
Unit tests for workflow service execution.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime

# Note: Imports are resolved through PYTHONPATH set in conftest.py
from app.workflow.executor import WorkflowExecutor


class TestWorkflowExecutor:
    """Test cases for WorkflowExecutor class"""
    
    def setup_method(self):
        """Setup test method"""
        self.executor = WorkflowExecutor()
    
    @patch('app.workflow.executor.temporal_client')
    async def test_execute_with_temporal(self, mock_temporal_client):
        """Test workflow execution with Temporal"""
        # Mock Temporal response
        mock_result = {"status": "success", "data": {"processed": True}}
        mock_handle = MagicMock()
        mock_handle.result.return_value = mock_result
        mock_temporal_client.start_workflow.return_value = mock_handle
        
        workflow_data = {
            "name": "Test Workflow",
            "nodes": [{"id": "1", "type": "trigger", "position": {"x": 0, "y": 0}, "data": {}}],
            "edges": []
        }
        user_id = "test-user-123"
        execution_id = "test-execution-123"
        
        result = await self.executor._execute_with_temporal(workflow_data, user_id, execution_id)
        
        assert "execution_id" in result
        assert "status" in result
        assert result["status"] == "completed"
    
    async def test_execute_locally(self):
        """Test local workflow execution"""
        workflow_data = {
            "name": "Test Workflow",
            "nodes": [
                {"id": "1", "type": "trigger", "position": {"x": 0, "y": 0}, "data": {}},
                {"id": "2", "type": "action", "position": {"x": 100, "y": 100}, "data": {}}
            ],
            "edges": [{"id": "1", "source": "1", "target": "2"}]
        }
        user_id = "test-user-123"
        execution_id = "test-execution-123"
        
        result = await self.executor._execute_locally(workflow_data, user_id, execution_id)
        
        assert "execution_id" in result
        assert "status" in result
        assert result["status"] == "completed"
        assert "output_data" in result
        assert result["output_data"]["workflow_name"] == "Test Workflow"
        assert result["output_data"]["node_count"] == 2
        assert result["output_data"]["edge_count"] == 1


if __name__ == "__main__":
    pytest.main([__file__])
