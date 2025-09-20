"""
Primitive validation for Flov7 AI service.
Validation logic for the 5-primitives system.
"""

from typing import Dict, Any, Optional, List, Tuple
from shared.utils.validators import validate_primitive_type, validate_primitive_schema
from shared.constants.primitives import PRIMITIVES
from shared.models.primitive import PrimitiveTypes, PrimitiveCategories
import logging

# Configure logging
logger = logging.getLogger(__name__)


class PrimitiveValidator:
    """Validator for primitive definitions and usage"""
    
    def __init__(self):
        self.primitives = PRIMITIVES
    
    def validate_primitive_structure(self, primitive_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate the structure of a primitive definition
        
        Args:
            primitive_data: Primitive definition data
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check required fields
            required_fields = ["name", "type", "display_name", "description"]
            for field in required_fields:
                if field not in primitive_data:
                    return False, f"Missing required field: {field}"
            
            # Validate primitive type
            primitive_type = primitive_data.get("type")
            if not validate_primitive_type(primitive_type):
                return False, f"Invalid primitive type: {primitive_type}"
            
            # Validate schemas if present
            config_schema = primitive_data.get("config_schema")
            if config_schema and not validate_primitive_schema(config_schema):
                return False, "Invalid config schema"
            
            input_schema = primitive_data.get("input_schema")
            if input_schema and not validate_primitive_schema(input_schema):
                return False, "Invalid input schema"
            
            output_schema = primitive_data.get("output_schema")
            if output_schema and not validate_primitive_schema(output_schema):
                return False, "Invalid output schema"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating primitive structure: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    def validate_workflow_primitives(self, workflow_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate that all primitives in a workflow are valid
        
        Args:
            workflow_data: Workflow definition data
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            nodes = workflow_data.get("nodes", [])
            
            for node in nodes:
                node_type = node.get("type")
                if not node_type:
                    return False, f"Node missing type field: {node.get('id', 'unknown')}"
                
                if node_type not in self.primitives:
                    return False, f"Invalid primitive type in node: {node_type}"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating workflow primitives: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    def get_primitive_compatibility(self, source_primitive: str, target_primitive: str) -> bool:
        """
        Check if two primitives are compatible for connection
        
        Args:
            source_primitive: Type of source primitive
            target_primitive: Type of target primitive
            
        Returns:
            Boolean indicating compatibility
        """
        # In a more complex implementation, this would check schema compatibility
        # For now, we'll assume all primitives can connect to all others
        return source_primitive in self.primitives and target_primitive in self.primitives
    
    def validate_primitive_chain(self, primitive_chain: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate a chain of primitives for logical flow
        
        Args:
            primitive_chain: List of primitive types in order
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check that all primitives are valid
            for primitive_type in primitive_chain:
                if primitive_type not in self.primitives:
                    return False, f"Invalid primitive type in chain: {primitive_type}"
            
            # Check that the chain starts with a trigger (in most cases)
            if primitive_chain and primitive_chain[0] != PrimitiveTypes.TRIGGER:
                logger.warning("Workflow chain does not start with a trigger primitive")
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating primitive chain: {str(e)}")
            return False, f"Validation error: {str(e)}"


# Global primitive validator instance
primitive_validator = PrimitiveValidator()
