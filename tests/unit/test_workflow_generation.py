"""
Unit tests for AI service workflow generation.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Note: Imports are resolved through PYTHONPATH set in conftest.py
from app.ai.workflow_generator import WorkflowGenerator


class TestWorkflowGenerator:
    """Test cases for WorkflowGenerator class"""
    
    def setup_method(self):
        """Setup test method"""
        self.generator = WorkflowGenerator()
    
    def test_enhance_workflow_adds_user_id(self):
        """Test that enhance_workflow adds user_id to workflow data"""
        workflow_data = {"name": "Test Workflow", "nodes": [], "edges": []}
        prompt = "Create a test workflow"
        user_id = "test-user-123"
        
        enhanced = self.generator._enhance_workflow(workflow_data, prompt, user_id)
        
        assert "user_id" in enhanced
        assert enhanced["user_id"] == user_id
    
    def test_generate_workflow_name_from_prompt(self):
        """Test that workflow names are generated from prompts"""
        prompt = "send email when new user signs up"
        expected_name = "Send Email When New User"
        
        name = self.generator._generate_workflow_name(prompt)
        
        assert name == expected_name
    
    def test_count_primitives(self):
        """Test that primitives are counted correctly"""
        workflow_data = {
            "nodes": [
                {"id": "1", "type": "trigger"},
                {"id": "2", "type": "action"},
                {"id": "3", "type": "condition"}
            ]
        }
        
        count = self.generator._count_primitives(workflow_data)
        
        assert count == 3
    
    @patch('ai.workflow_generator.openai_client')
    def test_create_workflow_from_prompt(self, mock_openai_client):
        """Test workflow creation from prompt"""
        # Mock OpenAI response
        mock_response = {
            "workflow": {
                "name": "Test Workflow",
                "nodes": [{"id": "1", "type": "trigger", "position": {"x": 0, "y": 0}, "data": {}}],
                "edges": []
            },
            "model": "gpt-4",
            "usage": {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300}
        }
        mock_openai_client.generate_workflow.return_value = mock_response
        
        prompt = "Create a simple workflow"
        user_id = "test-user-123"
        
        result = self.generator.create_workflow_from_prompt(prompt, user_id)
        
        assert "workflow" in result
        assert "ai_metadata" in result
        assert result["workflow"]["user_id"] == user_id
        assert result["workflow"]["status"] == "draft"


if __name__ == "__main__":
    pytest.main([__file__])
