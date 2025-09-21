"""
Comprehensive tests for the 5-primitives system implementation.
Tests for registry, executors, and template system.
"""

import pytest
import asyncio
from typing import Dict, Any
from datetime import datetime
from uuid import uuid4

# Import primitive system components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.primitives.registry import (
    PrimitiveRegistry, PrimitiveExecutionContext, primitive_registry
)
from shared.primitives.executors import (
    TriggerExecutor, ActionExecutor, ConnectionExecutor, 
    ConditionExecutor, DataExecutor
)
from shared.primitives.templates import template_manager
from shared.models.primitive import PrimitiveTypes


class TestPrimitiveRegistry:
    """Test the primitive registry system"""
    
    def test_registry_initialization(self):
        """Test registry initializes with built-in primitives"""
        registry = PrimitiveRegistry()
        
        assert registry.is_primitive_registered(PrimitiveTypes.TRIGGER)
        assert registry.is_primitive_registered(PrimitiveTypes.ACTION)
        assert registry.is_primitive_registered(PrimitiveTypes.CONNECTION)
        assert registry.is_primitive_registered(PrimitiveTypes.CONDITION)
        assert registry.is_primitive_registered(PrimitiveTypes.DATA)
    
    def test_get_executor(self):
        """Test getting executors for primitives"""
        registry = PrimitiveRegistry()
        
        trigger_executor = registry.get_executor(PrimitiveTypes.TRIGGER)
        assert trigger_executor is not None
        assert isinstance(trigger_executor, TriggerExecutor)
    
    def test_validate_workflow_primitives(self):
        """Test workflow primitive validation"""
        registry = PrimitiveRegistry()
        
        valid_workflow = {
            "nodes": [
                {"type": "trigger", "data": {"trigger_type": "manual"}},
                {"type": "action", "data": {"action_type": "email_send"}},
                {"type": "data", "data": {"operation_type": "transform"}}
            ]
        }
        
        is_valid, error = registry.validate_workflow_primitives(valid_workflow)
        assert is_valid is True
        assert error is None
    
    def test_validate_workflow_invalid_primitive(self):
        """Test validation with invalid primitive type"""
        registry = PrimitiveRegistry()
        
        invalid_workflow = {
            "nodes": [
                {"type": "invalid_type", "data": {}}
            ]
        }
        
        is_valid, error = registry.validate_workflow_primitives(invalid_workflow)
        assert is_valid is False
        assert "Unregistered primitive type" in error


class TestTriggerExecutor:
    """Test trigger primitive executor"""
    
    @pytest.fixture
    def trigger_executor(self):
        return TriggerExecutor()
    
    @pytest.fixture
    def context(self):
        return PrimitiveExecutionContext(
            execution_id=str(uuid4()),
            user_id="test_user"
        )
    
    @pytest.mark.asyncio
    async def test_manual_trigger(self, trigger_executor, context):
        """Test manual trigger execution"""
        config = {"trigger_type": "manual"}
        input_data = {"trigger_data": {"user": "test_user"}}
        
        result = await trigger_executor.execute(config, input_data, context)
        
        assert result["triggered"] is True
        assert result["trigger_type"] == "manual"
        assert result["initiated_by"] == "test_user"
    
    @pytest.mark.asyncio
    async def test_webhook_trigger(self, trigger_executor, context):
        """Test webhook trigger execution"""
        config = {"trigger_type": "webhook", "webhook_url": "/test-webhook"}
        input_data = {"trigger_data": {"payload": "test"}}
        
        result = await trigger_executor.execute(config, input_data, context)
        
        assert result["triggered"] is True
        assert result["trigger_type"] == "webhook"
        assert result["webhook_url"] == "/test-webhook"
    
    def test_validate_config(self, trigger_executor):
        """Test trigger configuration validation"""
        valid_config = {"trigger_type": "manual"}
        is_valid, error = trigger_executor.validate_config(valid_config)
        
        assert is_valid is True
        assert error is None
        
        invalid_config = {"trigger_type": "invalid"}
        is_valid, error = trigger_executor.validate_config(invalid_config)
        
        assert is_valid is False
        assert "Unsupported trigger type" in error


class TestActionExecutor:
    """Test action primitive executor"""
    
    @pytest.fixture
    def action_executor(self):
        return ActionExecutor()
    
    @pytest.fixture
    def context(self):
        return PrimitiveExecutionContext(
            execution_id=str(uuid4()),
            user_id="test_user"
        )
    
    @pytest.mark.asyncio
    async def test_ai_process_action(self, action_executor, context):
        """Test AI process action"""
        config = {
            "action_type": "ai_process",
            "prompt": "Summarize the data",
            "model": "gpt-3.5-turbo"
        }
        input_data = {"data": {"text": "This is a test document"}}
        
        result = await action_executor.execute(config, input_data, context)
        
        assert result["action_type"] == "ai_process"
        assert result["success"] is True
        assert "processed_data" in result["result"]
    
    @pytest.mark.asyncio
    async def test_wait_action(self, action_executor, context):
        """Test wait action"""
        config = {"action_type": "wait", "duration": 0.1, "unit": "seconds"}
        input_data = {}
        
        start_time = datetime.utcnow()
        result = await action_executor.execute(config, input_data, context)
        end_time = datetime.utcnow()
        
        assert result["action_type"] == "wait"
        assert result["success"] is True
        assert "waited_for" in result["result"]
        assert (end_time - start_time).total_seconds() >= 0.1
    
    def test_validate_config(self, action_executor):
        """Test action configuration validation"""
        valid_config = {"action_type": "email_send"}
        is_valid, error = action_executor.validate_config(valid_config)
        
        assert is_valid is True
        assert error is None


class TestConnectionExecutor:
    """Test connection primitive executor"""
    
    @pytest.fixture
    def connection_executor(self):
        return ConnectionExecutor()
    
    @pytest.fixture
    def context(self):
        return PrimitiveExecutionContext(
            execution_id=str(uuid4()),
            user_id="test_user"
        )
    
    @pytest.mark.asyncio
    async def test_database_connection(self, connection_executor, context):
        """Test database connection"""
        config = {
            "connection_type": "database",
            "connection_string": "sqlite://:memory:",
            "database_type": "sqlite"
        }
        input_data = {}
        
        result = await connection_executor.execute(config, input_data, context)
        
        assert result["connection_type"] == "database"
        assert result["connected"] is True
        assert "connection_id" in result
    
    @pytest.mark.asyncio
    async def test_slack_connection(self, connection_executor, context):
        """Test Slack connection"""
        config = {
            "connection_type": "slack",
            "workspace": "test-workspace",
            "channels": ["general", "alerts"]
        }
        input_data = {}
        
        result = await connection_executor.execute(config, input_data, context)
        
        assert result["connection_type"] == "slack"
        assert result["connected"] is True
        assert result["metadata"]["workspace"] == "test-workspace"
    
    def test_validate_config(self, connection_executor):
        """Test connection configuration validation"""
        valid_config = {"connection_type": "database", "connection_string": "test"}
        is_valid, error = connection_executor.validate_config(valid_config)
        
        assert is_valid is True
        assert error is None


class TestConditionExecutor:
    """Test condition primitive executor"""
    
    @pytest.fixture
    def condition_executor(self):
        return ConditionExecutor()
    
    @pytest.fixture
    def context(self):
        return PrimitiveExecutionContext(
            execution_id=str(uuid4()),
            user_id="test_user"
        )
    
    @pytest.mark.asyncio
    async def test_if_else_condition(self, condition_executor, context):
        """Test if-else condition"""
        config = {
            "condition_type": "if_else",
            "condition": "data.value > 10"
        }
        input_data = {"data": {"value": 15}}
        
        result = await condition_executor.execute(config, input_data, context)
        
        assert result["condition_type"] == "if_else"
        assert result["result"] is True
        assert result["branch"] == "true"
    
    @pytest.mark.asyncio
    async def test_filter_condition(self, condition_executor, context):
        """Test filter condition"""
        config = {
            "condition_type": "filter",
            "criteria": {"status": "active"}
        }
        input_data = {
            "data": [
                {"name": "item1", "status": "active"},
                {"name": "item2", "status": "inactive"},
                {"name": "item3", "status": "active"}
            ]
        }
        
        result = await condition_executor.execute(config, input_data, context)
        
        assert result["condition_type"] == "filter"
        assert result["result"] is True
        assert result["filtered_count"] == 2
        assert result["original_count"] == 3
    
    @pytest.mark.asyncio
    async def test_compare_condition(self, condition_executor, context):
        """Test compare condition"""
        config = {
            "condition_type": "compare",
            "field_a": "score",
            "field_b": "threshold",
            "operator": ">"
        }
        input_data = {"data": {"score": 85, "threshold": 80}}
        
        result = await condition_executor.execute(config, input_data, context)
        
        assert result["condition_type"] == "compare"
        assert result["result"] is True
        assert result["comparison"] == "85 > 80"


class TestDataExecutor:
    """Test data primitive executor"""
    
    @pytest.fixture
    def data_executor(self):
        return DataExecutor()
    
    @pytest.fixture
    def context(self):
        return PrimitiveExecutionContext(
            execution_id=str(uuid4()),
            user_id="test_user"
        )
    
    @pytest.mark.asyncio
    async def test_data_mapping(self, data_executor, context):
        """Test data mapping"""
        config = {
            "operation_type": "mapping",
            "mapping_rules": {
                "old_name": "new_name",
                "old_email": "email"
            }
        }
        input_data = {
            "data": {
                "old_name": "John Doe",
                "old_email": "john@example.com",
                "extra_field": "ignored"
            }
        }
        
        result = await data_executor.execute(config, input_data, context)
        
        assert result["operation_type"] == "mapping"
        assert result["result"]["new_name"] == "John Doe"
        assert result["result"]["email"] == "john@example.com"
        assert "extra_field" not in result["result"]
    
    @pytest.mark.asyncio
    async def test_data_filter(self, data_executor, context):
        """Test data filtering"""
        config = {
            "operation_type": "filter",
            "criteria": {"status": "active"}
        }
        input_data = {
            "data": [
                {"id": 1, "status": "active", "name": "Item 1"},
                {"id": 2, "status": "inactive", "name": "Item 2"},
                {"id": 3, "status": "active", "name": "Item 3"}
            ]
        }
        
        result = await data_executor.execute(config, input_data, context)
        
        assert result["operation_type"] == "filter"
        assert len(result["result"]) == 2
        assert all(item["status"] == "active" for item in result["result"])
    
    @pytest.mark.asyncio
    async def test_data_validation(self, data_executor, context):
        """Test data validation"""
        config = {
            "operation_type": "validate",
            "validation_rules": {
                "email": {"type": "string", "required": True},
                "age": {"type": "number", "min": 0, "max": 150}
            }
        }
        input_data = {
            "data": {
                "email": "test@example.com",
                "age": 25
            }
        }
        
        result = await data_executor.execute(config, input_data, context)
        
        assert result["operation_type"] == "validate"
        assert result["result"]["valid"] is True
        assert len(result["result"]["validation_results"]) == 2


class TestTemplateSystem:
    """Test primitive template system"""
    
    def test_template_initialization(self):
        """Test template manager initialization"""
        templates = template_manager.list_templates()
        assert len(templates) > 0
        
        trigger_templates = template_manager.get_templates_by_type("trigger")
        assert len(trigger_templates) > 0
    
    def test_search_templates(self):
        """Test template search"""
        results = template_manager.search_templates("email")
        assert len(results) > 0
        
        # Check that email-related templates are found
        email_templates = [t for t in results.values() if "email" in t["tags"]]
        assert len(email_templates) > 0
    
    def test_generate_primitive_config(self):
        """Test generating primitive configuration from template"""
        templates = template_manager.list_templates(primitive_type="trigger")
        template_id = list(templates.keys())[0]
        
        config = template_manager.generate_primitive_config(template_id, {
            "custom_field": "custom_value"
        })
        
        assert "_template" in config
        assert config["_template"]["id"] == template_id
        assert "custom_field" in config
    
    def test_create_custom_template(self):
        """Test creating custom template"""
        template_id = template_manager.create_custom_template(
            name="Custom Test Template",
            description="A custom template for testing",
            primitive_type="action",
            subtype="custom",
            config_template={"custom": True},
            tags=["test", "custom"]
        )
        
        template = template_manager.get_template(template_id)
        assert template is not None
        assert template.name == "Custom Test Template"


class TestIntegration:
    """Integration tests for the complete primitive system"""
    
    @pytest.fixture
    def context(self):
        return PrimitiveExecutionContext(
            execution_id=str(uuid4()),
            user_id="test_user"
        )
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow_execution(self, context):
        """Test complete workflow execution using primitives"""
        # 1. Trigger
        trigger_result = await primitive_registry.execute_primitive(
            "trigger",
            {"trigger_type": "manual"},
            {"trigger_data": {"user": "test_user"}},
            context
        )
        
        assert trigger_result["success"] is True
        
        # 2. Data processing
        data_result = await primitive_registry.execute_primitive(
            "data",
            {"operation_type": "transform", "transform_type": "json"},
            {"data": {"user": "test_user", "action": "process"}},
            context
        )
        
        assert data_result["success"] is True
        
        # 3. Action
        action_result = await primitive_registry.execute_primitive(
            "action",
            {"action_type": "notification", "channel": "test", "message": "Workflow completed"},
            {"data": data_result["data"]},
            context
        )
        
        assert action_result["success"] is True
    
    def test_workflow_validation(self):
        """Test complete workflow validation"""
        workflow = {
            "nodes": [
                {
                    "type": "trigger",
                    "data": {"trigger_type": "manual"}
                },
                {
                    "type": "condition",
                    "data": {"condition_type": "if_else", "condition": "data.valid == true"}
                },
                {
                    "type": "action",
                    "data": {"action_type": "email_send", "to_email": "test@example.com"}
                }
            ]
        }
        
        is_valid, error = primitive_registry.validate_workflow_primitives(workflow)
        assert is_valid is True
        assert error is None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
