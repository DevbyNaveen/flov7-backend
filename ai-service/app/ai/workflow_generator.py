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
from app.ai.openai_client import openai_client
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
        self.openai_client = openai_client
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
            
            # Use advanced prompts if enabled
            if self.config.enable_advanced_prompts:
                system_prompt = self.prompt_engine.generate_system_prompt()
                user_prompt = self.prompt_engine.generate_user_prompt(prompt, context)
            else:
                system_prompt = self._get_basic_system_prompt()
                user_prompt = prompt
            
            # Generate workflow using OpenAI with enhanced prompts
            result = await self._generate_workflow_with_ai(system_prompt, user_prompt, {"user_id": user_id})
            
            workflow_data = result["workflow"]
            
            # Validate generated workflow
            if not validate_workflow_json(workflow_data):
                raise ValueError("Generated workflow has invalid structure")
            
            # Enhance workflow with advanced metadata
            if self.config.enable_advanced_prompts:
                workflow_data = self.prompt_engine.enhance_workflow_with_metadata(workflow_data, prompt)
            
            # Enhance workflow with additional metadata
            enhanced_workflow = self._enhance_workflow(workflow_data, prompt, user_id)
            
            # Validate workflow quality
            quality_check = self.prompt_engine.validate_workflow_quality(enhanced_workflow)
            
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
                    "model": result.get("model", "gpt-4"),
                    "usage": result.get("usage", {}),
                    "quality_score": quality_check["score"],
                    "quality_issues": quality_check["issues"],
                    "advanced_prompts_used": self.config.enable_advanced_prompts
                },
                "database_result": db_result
            }
            
        except Exception as e:
            logger.error(f"Error creating workflow from prompt: {str(e)}")
            raise
    
    async def _generate_workflow_with_ai(self, system_prompt: str, user_prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate workflow using AI with enhanced prompts"""
        try:
            # Use the OpenAI client to generate workflow
            result = self.openai_client.generate_workflow_with_system_prompt(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                context=context
            )
            return result
        except Exception as e:
            logger.error(f"AI generation error: {str(e)}")
            # Fallback to basic generation
            return self.openai_client.generate_workflow(user_prompt, context)
    
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
