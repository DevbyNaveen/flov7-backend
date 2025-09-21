"""
Integration tests for AI service functionality.
Tests the complete workflow generation pipeline with database persistence.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.ai.workflow_generator import workflow_generator
from app.ai.advanced_prompts import advanced_prompt_engine
from app.config import config


class TestAIServiceIntegration:
    """Integration tests for AI service"""
    
    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response"""
        return {
            "workflow": {
                "name": "Test Workflow",
                "description": "A test workflow for integration testing",
                "nodes": [
                    {
                        "id": "trigger_1",
                        "type": "trigger",
                        "position": {"x": 100, "y": 100},
                        "data": {
                            "label": "HTTP Webhook",
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
                            "label": "Process Data",
                            "config": {
                                "action_type": "data_transform",
                                "transformation": "uppercase"
                            }
                        }
                    }
                ],
                "edges": [
                    {
                        "id": "edge_1",
                        "source": "trigger_1",
                        "target": "action_1"
                    }
                ]
            },
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 300,
                "total_tokens": 450
            },
            "model": "gpt-4"
        }
    
    @pytest.fixture
    def mock_database_response(self):
        """Mock database response"""
        return {
            "success": True,
            "data": {
                "id": "test-workflow-id",
                "created_at": "2025-09-21T03:28:00Z",
                "name": "Test Workflow",
                "status": "draft"
            }
        }
    
    @pytest.mark.asyncio
    async def test_workflow_generation_with_database_persistence(self, mock_openai_response, mock_database_response):
        """Test complete workflow generation with database persistence"""
        
        # Mock OpenAI client
        with patch.object(workflow_generator.openai_client, 'generate_workflow_with_system_prompt', return_value=mock_openai_response):
            # Mock database operations
            with patch.object(workflow_generator.workflow_crud, 'create_workflow', return_value=mock_database_response):
                # Mock API Gateway notification
                with patch('app.ai.workflow_generator.api_gateway_client') as mock_gateway:
                    mock_gateway.__aenter__ = AsyncMock(return_value=mock_gateway)
                    mock_gateway.__aexit__ = AsyncMock(return_value=None)
                    mock_gateway.notify_workflow_generated = AsyncMock(return_value={"success": True})
                    
                    # Test workflow generation
                    result = await workflow_generator.create_workflow_from_prompt(
                        prompt="Create a workflow to process incoming webhook data",
                        user_id="test-user-123",
                        save_to_db=True
                    )
                    
                    # Assertions
                    assert result["workflow"]["name"] == "Test Workflow"
                    assert result["workflow"]["id"] == "test-workflow-id"
                    assert result["ai_metadata"]["quality_score"] > 0
                    assert result["database_result"]["success"] is True
    
    @pytest.mark.asyncio
    async def test_advanced_prompts_integration(self):
        """Test advanced prompts functionality"""
        
        # Test system prompt generation
        system_prompt = advanced_prompt_engine.generate_system_prompt()
        assert "5-PRIMITIVES SYSTEM" in system_prompt
        assert "trigger" in system_prompt.lower()
        assert "action" in system_prompt.lower()
        
        # Test user prompt enhancement
        user_prompt = advanced_prompt_engine.generate_user_prompt(
            "Create an email automation workflow",
            context={"user_industry": "marketing", "technical_level": "beginner"}
        )
        assert "email automation workflow" in user_prompt
        assert "marketing" in user_prompt
        assert "beginner" in user_prompt
    
    @pytest.mark.asyncio
    async def test_workflow_quality_validation(self):
        """Test workflow quality validation"""
        
        # Test valid workflow
        valid_workflow = {
            "name": "Valid Workflow",
            "description": "A valid test workflow",
            "nodes": [
                {
                    "id": "trigger_1",
                    "type": "trigger",
                    "position": {"x": 100, "y": 100},
                    "data": {"label": "Test Trigger"}
                }
            ],
            "edges": []
        }
        
        quality_result = advanced_prompt_engine.validate_workflow_quality(valid_workflow)
        assert quality_result["score"] > 50
        assert quality_result["quality"] in ["fair", "good", "excellent"]
        
        # Test invalid workflow
        invalid_workflow = {
            "name": "Invalid Workflow"
            # Missing required fields
        }
        
        quality_result = advanced_prompt_engine.validate_workflow_quality(invalid_workflow)
        assert quality_result["score"] < 50
        assert len(quality_result["issues"]) > 0
    
    @pytest.mark.asyncio
    async def test_workflow_database_operations(self, mock_database_response):
        """Test workflow database operations"""
        
        with patch.object(workflow_generator.workflow_crud, 'get_workflow', return_value=mock_database_response):
            result = await workflow_generator.get_workflow_from_database("test-id", "test-user")
            assert result["success"] is True
            assert result["data"]["id"] == "test-workflow-id"
        
        with patch.object(workflow_generator.workflow_crud, 'list_workflows', return_value={"success": True, "data": []}):
            result = await workflow_generator.list_user_workflows("test-user")
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_workflow_regeneration(self, mock_openai_response, mock_database_response):
        """Test workflow regeneration functionality"""
        
        # Mock existing workflow
        existing_workflow = {
            "success": True,
            "data": {
                "id": "existing-id",
                "description": "Original workflow description",
                "workflow_json": {"nodes": [], "edges": []}
            }
        }
        
        with patch.object(workflow_generator.workflow_crud, 'get_workflow', return_value=existing_workflow):
            with patch.object(workflow_generator, 'create_workflow_from_prompt', return_value={"workflow": mock_openai_response["workflow"], "ai_metadata": {}}):
                with patch.object(workflow_generator.workflow_crud, 'update_workflow', return_value={"success": True, "data": {}}):
                    
                    result = await workflow_generator.regenerate_workflow(
                        "existing-id", 
                        "test-user", 
                        "New improved prompt"
                    )
                    
                    assert result["success"] is True
                    assert "workflow" in result
    
    def test_configuration_validation(self):
        """Test AI service configuration"""
        
        # Test configuration initialization
        assert hasattr(config, 'enable_database_persistence')
        assert hasattr(config, 'enable_advanced_prompts')
        assert hasattr(config, 'max_workflow_complexity')
        
        # Test database client access
        if config.enable_database_persistence:
            try:
                db_client = config.get_database_client()
                assert db_client is not None
            except ValueError:
                # Expected if database is not configured
                pass
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in workflow generation"""
        
        # Test with invalid OpenAI response
        with patch.object(workflow_generator.openai_client, 'generate_workflow_with_system_prompt', side_effect=Exception("API Error")):
            with pytest.raises(Exception):
                await workflow_generator.create_workflow_from_prompt(
                    "Test prompt",
                    "test-user",
                    save_to_db=False
                )
        
        # Test with database error
        with patch.object(workflow_generator.openai_client, 'generate_workflow_with_system_prompt', return_value={"workflow": {"name": "Test", "nodes": [], "edges": []}}):
            with patch.object(workflow_generator.workflow_crud, 'create_workflow', return_value={"success": False, "error": "Database error"}):
                
                result = await workflow_generator.create_workflow_from_prompt(
                    "Test prompt",
                    "test-user",
                    save_to_db=True
                )
                
                # Should still return workflow even if database save fails
                assert "workflow" in result
                assert result["database_result"]["success"] is False


if __name__ == "__main__":
    pytest.main([__file__])
