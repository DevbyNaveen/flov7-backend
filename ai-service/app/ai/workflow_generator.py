"""
Workflow generator for Flov7 AI service.
Converts natural language prompts to workflow definitions using the 5-primitives system.
Enhanced with database persistence and advanced AI prompts.
"""

from typing import Dict, Any, Optional, List
import sys
import os
import asyncio
from datetime import datetime
from app.ai.enhanced_openai_client import enhanced_openai_client
from app.ai.advanced_prompts import advanced_prompt_engine
from app.config import config
from app.integration.api_gateway_client import api_gateway_client
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared.constants.primitives import PRIMITIVES
from shared.utils.validators import validate_workflow_json
from shared.crud.workflows import workflow_crud

# Configure logging
logger = logging.getLogger(__name__)


class WorkflowGenerator:
    """Enhanced AI-powered workflow generator with database persistence"""
    
    def __init__(self):
        self.openai_client = enhanced_openai_client
        self.prompt_engine = advanced_prompt_engine
        self.config = config
        self.workflow_crud = workflow_crud
    
    async def create_workflow_from_prompt(self, prompt: str, user_id: str, context: Optional[Dict[str, Any]] = None, save_to_db: bool = True) -> Dict[str, Any]:
        """
        Create a workflow from a natural language prompt with enhanced AI and database persistence
        
        Args:
            prompt: Natural language description of the workflow
            user_id: ID of the user requesting the workflow
            context: Additional context for workflow generation
            save_to_db: Whether to save the workflow to database
            
        Returns:
            Dict containing the workflow data and metadata
        """
        try:
            logger.info(f"Generating workflow for user {user_id}: {prompt[:100]}...")
            
            # Prepare context for AI generation
            generation_context = {
                "user_id": user_id,
                "prompt": prompt,
                **(context or {})
            }
            
            # Use enhanced AI client for generation with validation
            result = await enhanced_openai_client.generate_workflow_with_validation(
                prompt=prompt,
                context=generation_context
            )
            
            workflow_data = result["workflow"]
            
            # Additional validation using our validation system
            structure_validation = self.validate_workflow_structure(workflow_data)
            if not structure_validation:
                # Try to fix structure issues
                workflow_data = await self._auto_fix_workflow_structure(workflow_data)
                structure_validation = self.validate_workflow_structure(workflow_data)
                if not structure_validation:
                    raise ValueError("Generated workflow has invalid structure that cannot be fixed")
            
            # Enhance workflow with additional metadata
            enhanced_workflow = self._enhance_workflow(workflow_data, prompt, user_id)
            
            # Validate workflow quality using both systems
            quality_check = self.prompt_engine.validate_workflow_quality(enhanced_workflow)
            ai_validation = result.get("validation", {})
            
            # Combine validation results
            final_quality_score = min(quality_check["score"], 100 if ai_validation.get("valid", True) else 50)
            
            # Save to database if enabled and requested
            db_result = None
            if save_to_db and self.config.enable_database_persistence:
                try:
                    db_result = await self._save_workflow_to_database(enhanced_workflow, user_id)
                    if db_result["success"]:
                        enhanced_workflow["id"] = db_result["data"]["id"]
                        enhanced_workflow["created_at"] = db_result["data"]["created_at"]
                        logger.info(f"Workflow saved to database with ID: {enhanced_workflow['id']}")
                        
                        # Notify API Gateway about workflow generation
                        try:
                            async with api_gateway_client as gateway:
                                await gateway.notify_workflow_generated(enhanced_workflow, user_id)
                        except Exception as gateway_error:
                            logger.warning(f"Failed to notify API Gateway: {str(gateway_error)}")
                    else:
                        logger.warning(f"Failed to save workflow to database: {db_result['error']}")
                except Exception as db_error:
                    logger.error(f"Database save error: {str(db_error)}")
                    # Continue without database save
            
            return {
                "workflow": enhanced_workflow,
                "ai_metadata": {
                    "model": result.get("model", "enhanced_ai"),
                    "usage": result.get("usage", {}),
                    "quality_score": final_quality_score,
                    "quality_issues": quality_check["issues"],
                    "validation_result": ai_validation,
                    "advanced_prompts_used": self.config.enable_advanced_prompts,
                    "generation_method": result.get("generation_method", "unknown")
                },
                "database_result": db_result
            }
            
        except Exception as e:
            logger.error(f"Error creating workflow from prompt: {str(e)}")
            raise
    
    async def _generate_workflow_with_ai(self, system_prompt: str, user_prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate workflow using enhanced AI client"""
        try:
            # Use enhanced AI client for better generation
            result = await enhanced_openai_client.generate_workflow_with_validation(
                prompt=user_prompt,
                context=context
            )
            return result
        except Exception as e:
            logger.error(f"AI generation error: {str(e)}")
            raise
    
    async def _save_workflow_to_database(self, workflow_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Save workflow to database using CRUD operations"""
        try:
            # Prepare workflow data for database
            db_workflow_data = {
                "name": workflow_data.get("name", "Untitled Workflow"),
                "description": workflow_data.get("description", ""),
                "workflow_json": {
                    "nodes": workflow_data.get("nodes", []),
                    "edges": workflow_data.get("edges", []),
                    "metadata": workflow_data.get("metadata", {})
                },
                "status": workflow_data.get("status", "draft"),
                "tags": workflow_data.get("metadata", {}).get("tags", [])
            }
            
            # Save using workflow CRUD
            result = await self.workflow_crud.create_workflow(user_id, db_workflow_data)
            return result
            
        except Exception as e:
            logger.error(f"Database save error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _get_basic_system_prompt(self) -> str:
        """Get basic system prompt for workflow generation"""
        return """You are an AI workflow generator for the Flov7 platform. Create workflows using the 5-primitives system: trigger, action, connection, condition, data.

Return a JSON workflow with:
- name: workflow name
- description: workflow description  
- nodes: array of nodes with id, type, position {x, y}, data
- edges: array of edges with id, source, target

Use only these primitive types: trigger, action, connection, condition, data."""
    
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
        
        # Add generation timestamp
        workflow_data["generated_at"] = datetime.utcnow().isoformat()
        
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
    
    async def get_workflow_from_database(self, workflow_id: str, user_id: str) -> Dict[str, Any]:
        """Retrieve workflow from database"""
        try:
            if not self.config.enable_database_persistence:
                return {"success": False, "error": "Database persistence is disabled"}
            
            result = await self.workflow_crud.get_workflow(workflow_id, user_id)
            return result
        except Exception as e:
            logger.error(f"Error retrieving workflow from database: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_workflow_in_database(self, workflow_id: str, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update workflow in database"""
        try:
            if not self.config.enable_database_persistence:
                return {"success": False, "error": "Database persistence is disabled"}
            
            result = await self.workflow_crud.update_workflow(workflow_id, user_id, update_data)
            return result
        except Exception as e:
            logger.error(f"Error updating workflow in database: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def list_user_workflows(self, user_id: str, skip: int = 0, limit: int = 50, status: Optional[str] = None) -> Dict[str, Any]:
        """List workflows for a user"""
        try:
            if not self.config.enable_database_persistence:
                return {"success": False, "error": "Database persistence is disabled"}
            
            result = await self.workflow_crud.list_workflows(user_id, skip, limit, status)
            return result
        except Exception as e:
            logger.error(f"Error listing workflows: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def regenerate_workflow(self, workflow_id: str, user_id: str, new_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Regenerate an existing workflow with improvements"""
        try:
            # Get existing workflow
            existing_result = await self.get_workflow_from_database(workflow_id, user_id)
            if not existing_result["success"]:
                return existing_result
            
            existing_workflow = existing_result["data"]
            
            # Use new prompt or existing description
            prompt = new_prompt or existing_workflow.get("description", "")
            
            # Create context from existing workflow
            context = {
                "existing_workflow": existing_workflow,
                "regeneration": True,
                "preserve_structure": True
            }
            
            # Generate new workflow
            new_workflow_result = await self.create_workflow_from_prompt(
                prompt, user_id, context, save_to_db=False
            )
            
            if new_workflow_result:
                # Update existing workflow with new data
                update_data = {
                    "workflow_json": new_workflow_result["workflow"],
                    "description": prompt
                }
                
                update_result = await self.update_workflow_in_database(workflow_id, user_id, update_data)
                
                return {
                    "success": True,
                    "workflow": new_workflow_result["workflow"],
                    "ai_metadata": new_workflow_result["ai_metadata"],
                    "update_result": update_result
                }
            
            return {"success": False, "error": "Failed to regenerate workflow"}
            
        except Exception as e:
            logger.error(f"Error regenerating workflow: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _auto_fix_workflow_structure(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically fix common workflow structure issues"""
        try:
            # Ensure required fields
            if "name" not in workflow:
                workflow["name"] = "Generated Workflow"
            
            if "description" not in workflow:
                workflow["description"] = "Automatically generated workflow"
            
            if "nodes" not in workflow:
                workflow["nodes"] = []
            
            if "edges" not in workflow:
                workflow["edges"] = []
            
            # Ensure metadata exists
            if "metadata" not in workflow:
                workflow["metadata"] = {}
            
            # Fix node structure
            nodes = workflow.get("nodes", [])
            for i, node in enumerate(nodes):
                if not isinstance(node, dict):
                    nodes[i] = {"id": f"node_{i}", "type": "action", "data": {}}
                
                if "id" not in node:
                    node["id"] = f"node_{i}"
                
                if "type" not in node or node["type"] not in {"trigger", "action", "connection", "condition", "data"}:
                    node["type"] = "action"
                
                if "position" not in node:
                    node["position"] = {"x": 100 + (i * 300), "y": 100}
                
                if "data" not in node:
                    node["data"] = {"label": node.get("id", f"Node {i}")}
            
            # Fix edge structure
            edges = workflow.get("edges", [])
            node_ids = {node.get("id") for node in nodes if "id" in node}
            
            valid_edges = []
            for i, edge in enumerate(edges):
                if isinstance(edge, dict) and "source" in edge and "target" in edge:
                    if edge["source"] in node_ids and edge["target"] in node_ids:
                        if "id" not in edge:
                            edge["id"] = f"edge_{i}"
                        valid_edges.append(edge)
            
            workflow["edges"] = valid_edges
            
            return workflow
            
        except Exception as e:
            logger.error(f"Error auto-fixing workflow structure: {str(e)}")
            return workflow
    
    def validate_workflow_structure(self, workflow_data: Dict[str, Any]) -> bool:
        """Enhanced validation of the workflow structure"""
        try:
            # Check required top-level fields
            required_fields = ["name", "description", "nodes", "edges"]
            for field in required_fields:
                if field not in workflow_data:
                    return False
            
            # Validate nodes
            nodes = workflow_data.get("nodes", [])
            if not isinstance(nodes, list) or len(nodes) == 0:
                return False
            
            valid_types = {"trigger", "action", "connection", "condition", "data"}
            has_trigger = False
            
            for node in nodes:
                if not isinstance(node, dict):
                    return False
                
                if "type" not in node or node["type"] not in valid_types:
                    return False
                
                if node["type"] == "trigger":
                    has_trigger = True
                
                if "id" not in node or "position" not in node or "data" not in node:
                    return False
            
            # Must have at least one trigger
            if not has_trigger:
                return False
            
            # Validate edges
            edges = workflow_data.get("edges", [])
            if not isinstance(edges, list):
                return False
            
            node_ids = {node.get("id") for node in nodes if "id" in node}
            for edge in edges:
                if not isinstance(edge, dict):
                    return False
                
                if "source" not in edge or "target" not in edge:
                    return False
                
                if edge["source"] not in node_ids or edge["target"] not in node_ids:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Workflow validation error: {str(e)}")
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
