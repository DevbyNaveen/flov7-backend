"""
Workflow generator for Flov7 AI service.
Converts natural language prompts to workflow definitions using the 5-primitives system.
"""

from typing import Dict, Any, Optional, List
from app.ai.openai_client import openai_client
from shared.constants.primitives import PRIMITIVES
from shared.models.workflow import WorkflowCreate
from shared.utils.validators import validate_workflow_json
import logging

# Configure logging
logger = logging.getLogger(__name__)


class WorkflowGenerator:
    """AI-powered workflow generator"""
    
    def __init__(self):
        self.openai_client = openai_client
    
    def create_workflow_from_prompt(self, prompt: str, user_id: str) -> Dict[str, Any]:
        """
        Create a workflow from a natural language prompt
        
        Args:
            prompt: Natural language description of the workflow
            user_id: ID of the user requesting the workflow
            
        Returns:
            Dict containing the workflow data and metadata
        """
        try:
            # Generate workflow using OpenAI
            result = self.openai_client.generate_workflow(prompt, {"user_id": user_id})
            
            workflow_data = result["workflow"]
            
            # Validate generated workflow
            if not validate_workflow_json(workflow_data):
                raise ValueError("Generated workflow has invalid structure")
            
            # Enhance workflow with metadata
            enhanced_workflow = self._enhance_workflow(workflow_data, prompt, user_id)
            
            return {
                "workflow": enhanced_workflow,
                "ai_metadata": {
                    "model": result["model"],
                    "usage": result["usage"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating workflow from prompt: {str(e)}")
            raise
    
    def _enhance_workflow(self, workflow_data: Dict[str, Any], prompt: str, user_id: str) -> Dict[str, Any]:
        """Enhance the generated workflow with additional metadata and validation"""
        
        # Ensure workflow has a name
        if "name" not in workflow_data:
            workflow_data["name"] = self._generate_workflow_name(prompt)
        
        # Ensure workflow has a description
        if "description" not in workflow_data:
            workflow_data["description"] = prompt
        
        # Validate and count primitives
        primitives_count = self._count_primitives(workflow_data)
        workflow_data["primitives_count"] = primitives_count
        
        # Add user context
        workflow_data["user_id"] = user_id
        
        # Set initial status
        workflow_data["status"] = "draft"
        
        return workflow_data
    
    def _generate_workflow_name(self, prompt: str) -> str:
        """Generate a workflow name from the prompt"""
        # Simple approach: take first few words and title case them
        words = prompt.split()[:5]
        return " ".join(words).title()
    
    def _count_primitives(self, workflow_data: Dict[str, Any]) -> int:
        """Count the number of primitives in the workflow"""
        nodes = workflow_data.get("nodes", [])
        return len(nodes)
    
    def validate_workflow_structure(self, workflow_data: Dict[str, Any]) -> bool:
        """Validate the workflow structure against Flov7 primitives system"""
        try:
            # Check if workflow has required fields
            required_fields = ["name", "nodes", "edges"]
            for field in required_fields:
                if field not in workflow_data:
                    return False
            
            # Validate nodes
            nodes = workflow_data.get("nodes", [])
            for node in nodes:
                if not self._validate_node(node):
                    return False
            
            # Validate edges
            edges = workflow_data.get("edges", [])
            for edge in edges:
                if not self._validate_edge(edge):
                    return False
            
            return True
        except Exception:
            return False
    
    def _validate_node(self, node: Dict[str, Any]) -> bool:
        """Validate a workflow node"""
        required_fields = ["id", "type", "position", "data"]
        for field in required_fields:
            if field not in node:
                return False
        
        # Validate node type is one of the 5 primitives
        node_type = node.get("type")
        if node_type not in PRIMITIVES:
            return False
        
        # Validate position has x, y
        position = node.get("position", {})
        if "x" not in position or "y" not in position:
            return False
        
        return True
    
    def _validate_edge(self, edge: Dict[str, Any]) -> bool:
        """Validate a workflow edge"""
        required_fields = ["id", "source", "target"]
        for field in required_fields:
            if field not in edge:
                return False
        
        return True


# Global workflow generator instance
workflow_generator = WorkflowGenerator()
