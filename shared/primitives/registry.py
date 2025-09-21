"""
Primitive Registry for Flov7 platform.
Runtime registry system for managing and executing the 5-primitives system.
"""

from typing import Dict, Any, Optional, List, Callable, Type
from abc import ABC, abstractmethod
import logging
import asyncio
from datetime import datetime
from uuid import UUID, uuid4

from shared.constants.primitives import PRIMITIVES
from shared.models.primitive import PrimitiveTypes
from shared.utils.validators import validate_primitive_schema

logger = logging.getLogger(__name__)


class PrimitiveExecutionContext:
    """Context object passed to primitive executors during execution"""
    
    def __init__(self, 
                 execution_id: str,
                 user_id: str,
                 workflow_id: Optional[str] = None,
                 node_id: Optional[str] = None,
                 previous_outputs: Optional[Dict[str, Any]] = None,
                 global_context: Optional[Dict[str, Any]] = None):
        self.execution_id = execution_id
        self.user_id = user_id
        self.workflow_id = workflow_id
        self.node_id = node_id
        self.previous_outputs = previous_outputs or {}
        self.global_context = global_context or {}
        self.start_time = datetime.utcnow()
        self.metadata = {}
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to the execution context"""
        self.metadata[key] = value
    
    def get_execution_time(self) -> float:
        """Get elapsed execution time in seconds"""
        return (datetime.utcnow() - self.start_time).total_seconds()


class PrimitiveExecutor(ABC):
    """Abstract base class for primitive executors"""
    
    @abstractmethod
    async def execute(self, 
                     config: Dict[str, Any], 
                     input_data: Dict[str, Any], 
                     context: PrimitiveExecutionContext) -> Dict[str, Any]:
        """
        Execute the primitive with given configuration and input data
        
        Args:
            config: Primitive configuration
            input_data: Input data for the primitive
            context: Execution context
            
        Returns:
            Dictionary containing execution results
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate primitive configuration
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """Get the input schema for this primitive"""
        pass
    
    @abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        """Get the output schema for this primitive"""
        pass


class PrimitiveRegistry:
    """Central registry for managing primitive executors"""
    
    def __init__(self):
        self._executors: Dict[str, PrimitiveExecutor] = {}
        self._primitive_configs: Dict[str, Dict[str, Any]] = {}
        self._templates: Dict[str, Dict[str, Any]] = {}
        self._validation_cache: Dict[str, bool] = {}
        
        # Initialize with built-in primitives
        self._initialize_builtin_primitives()
    
    def _initialize_builtin_primitives(self):
        """Initialize built-in primitive executors"""
        from .executors.trigger_executor import TriggerExecutor
        from .executors.action_executor import ActionExecutor
        from .executors.connection_executor import ConnectionExecutor
        from .executors.condition_executor import ConditionExecutor
        from .executors.data_executor import DataExecutor
        
        # Register built-in executors
        self.register_executor(PrimitiveTypes.TRIGGER, TriggerExecutor())
        self.register_executor(PrimitiveTypes.ACTION, ActionExecutor())
        self.register_executor(PrimitiveTypes.CONNECTION, ConnectionExecutor())
        self.register_executor(PrimitiveTypes.CONDITION, ConditionExecutor())
        self.register_executor(PrimitiveTypes.DATA, DataExecutor())
        
        # Load primitive configurations
        for primitive_type, config in PRIMITIVES.items():
            self._primitive_configs[primitive_type] = config
    
    def register_executor(self, primitive_type: str, executor: PrimitiveExecutor):
        """Register a primitive executor"""
        if not isinstance(executor, PrimitiveExecutor):
            raise ValueError(f"Executor must be an instance of PrimitiveExecutor")
        
        self._executors[primitive_type] = executor
        logger.info(f"Registered executor for primitive type: {primitive_type}")
    
    def get_executor(self, primitive_type: str) -> Optional[PrimitiveExecutor]:
        """Get executor for a primitive type"""
        return self._executors.get(primitive_type)
    
    def list_executors(self) -> List[str]:
        """List all registered primitive types"""
        return list(self._executors.keys())
    
    def is_primitive_registered(self, primitive_type: str) -> bool:
        """Check if a primitive type is registered"""
        return primitive_type in self._executors
    
    async def execute_primitive(self,
                              primitive_type: str,
                              config: Dict[str, Any],
                              input_data: Dict[str, Any],
                              context: PrimitiveExecutionContext) -> Dict[str, Any]:
        """
        Execute a primitive with the given configuration
        
        Args:
            primitive_type: Type of primitive to execute
            config: Primitive configuration
            input_data: Input data for the primitive
            context: Execution context
            
        Returns:
            Execution results
            
        Raises:
            ValueError: If primitive type is not registered
            RuntimeError: If execution fails
        """
        executor = self.get_executor(primitive_type)
        if not executor:
            raise ValueError(f"No executor registered for primitive type: {primitive_type}")
        
        # Validate configuration
        is_valid, error_msg = executor.validate_config(config)
        if not is_valid:
            raise ValueError(f"Invalid configuration for {primitive_type}: {error_msg}")
        
        # Validate input data against schema
        input_schema = executor.get_input_schema()
        if input_schema:
            is_valid, error_msg = validate_primitive_schema(input_data, input_schema)
            if not is_valid:
                raise ValueError(f"Invalid input data: {error_msg}")
        
        try:
            # Execute the primitive
            result = await executor.execute(config, input_data, context)
            
            # Validate output data against schema
            output_schema = executor.get_output_schema()
            if output_schema:
                is_valid, error_msg = validate_primitive_schema(result, output_schema)
                if not is_valid:
                    logger.warning(f"Output validation failed for {primitive_type}: {error_msg}")
            
            return {
                "success": True,
                "data": result,
                "metadata": {
                    "primitive_type": primitive_type,
                    "execution_time": context.get_execution_time(),
                    "node_id": context.node_id
                }
            }
            
        except Exception as e:
            logger.error(f"Error executing primitive {primitive_type}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "primitive_type": primitive_type,
                    "execution_time": context.get_execution_time(),
                    "node_id": context.node_id
                }
            }
    
    def register_template(self, template_name: str, template_config: Dict[str, Any]):
        """Register a primitive template"""
        self._templates[template_name] = template_config
        logger.info(f"Registered template: {template_name}")
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get a registered template"""
        return self._templates.get(template_name)
    
    def list_templates(self) -> List[str]:
        """List all registered templates"""
        return list(self._templates.keys())
    
    def get_primitive_info(self, primitive_type: str) -> Optional[Dict[str, Any]]:
        """Get information about a primitive type"""
        if primitive_type not in self._executors:
            return None
        
        executor = self._executors[primitive_type]
        config = self._primitive_configs.get(primitive_type, {})
        
        return {
            "type": primitive_type,
            "config": config,
            "input_schema": executor.get_input_schema(),
            "output_schema": executor.get_output_schema(),
            "registered": True
        }
    
    def validate_workflow_primitives(self, workflow_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate all primitives in a workflow"""
        try:
            nodes = workflow_data.get("nodes", [])
            
            for node in nodes:
                node_type = node.get("type")
                if not node_type:
                    return False, f"Node missing type field: {node.get('id', 'unknown')}"
                
                if not self.is_primitive_registered(node_type):
                    return False, f"Unregistered primitive type: {node_type}"
                
                # Validate node configuration
                node_config = node.get("data", {})
                executor = self.get_executor(node_type)
                if executor:
                    is_valid, error_msg = executor.validate_config(node_config)
                    if not is_valid:
                        return False, f"Invalid configuration for {node_type}: {error_msg}"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating workflow primitives: {str(e)}")
            return False, str(e)


# Global registry instance
primitive_registry = PrimitiveRegistry()
