"""
Unit tests for primitive management.
"""

import pytest
import os
import sys

# Note: Imports are resolved through PYTHONPATH set in conftest.py
from app.primitives.primitives import PrimitiveManager
from app.primitives.validation import PrimitiveValidator


class TestPrimitiveManager:
    """Test cases for PrimitiveManager class"""
    
    def setup_method(self):
        """Setup test method"""
        self.manager = PrimitiveManager()
    
    def test_get_all_primitives(self):
        """Test that all primitives are returned"""
        primitives = self.manager.get_all_primitives()
        
        assert len(primitives) == 5
        assert "trigger" in primitives
        assert "action" in primitives
        assert "connection" in primitives
        assert "condition" in primitives
        assert "data" in primitives
    
    def test_get_primitive(self):
        """Test that individual primitives can be retrieved"""
        trigger = self.manager.get_primitive("trigger")
        
        assert trigger is not None
        assert trigger["name"] == "trigger"
        assert trigger["display_name"] == "Trigger"
    
    def test_get_primitive_types(self):
        """Test that primitive types are returned correctly"""
        types = self.manager.get_primitive_types()
        
        assert len(types) == 5
        assert "trigger" in types
        assert "action" in types


class TestPrimitiveValidator:
    """Test cases for PrimitiveValidator class"""
    
    def setup_method(self):
        """Setup test method"""
        self.validator = PrimitiveValidator()
    
    def test_validate_primitive_structure_valid(self):
        """Test that valid primitive structures pass validation"""
        primitive_data = {
            "name": "test_trigger",
            "type": "trigger",
            "display_name": "Test Trigger",
            "description": "A test trigger primitive"
        }
        
        is_valid, error = self.validator.validate_primitive_structure(primitive_data)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_primitive_structure_invalid_type(self):
        """Test that invalid primitive types fail validation"""
        primitive_data = {
            "name": "test_invalid",
            "type": "invalid_type",
            "display_name": "Test Invalid",
            "description": "An invalid primitive"
        }
        
        is_valid, error = self.validator.validate_primitive_structure(primitive_data)
        
        assert is_valid is False
        assert error is not None
    
    def test_validate_workflow_primitives(self):
        """Test that workflow primitives are validated correctly"""
        workflow_data = {
            "nodes": [
                {"id": "1", "type": "trigger", "position": {"x": 0, "y": 0}, "data": {}},
                {"id": "2", "type": "action", "position": {"x": 100, "y": 100}, "data": {}}
            ]
        }
        
        is_valid, error = self.validator.validate_workflow_primitives(workflow_data)
        
        assert is_valid is True
        assert error is None


if __name__ == "__main__":
    pytest.main([__file__])
