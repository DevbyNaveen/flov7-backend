"""
Enhanced OpenAI client for Flov7 AI service.
Provides robust AI integration with fallback mechanisms and advanced validation.
"""

import openai
import sys
import os
from typing import Optional, Dict, Any, List
import logging
import json
import asyncio
from datetime import datetime
import httpx

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)


class EnhancedOpenAIClient:
    """Enhanced OpenAI client with fallback mechanisms and validation"""
    
    def __init__(self):
        self.client: Optional[openai.OpenAI] = None
        self.async_client: Optional[openai.AsyncOpenAI] = None
        self._initialize_clients()
        self.fallback_enabled = True
        self.validation_enabled = True
    
    def _initialize_clients(self):
        """Initialize both sync and async OpenAI clients"""
        if settings.OPENAI_API_KEY:
            try:
                self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                self.async_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI clients initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI clients: {str(e)}")
                self.client = None
                self.async_client = None
        else:
            logger.warning("OpenAI API key not configured. AI features will use fallback mode.")
    
    def is_available(self) -> bool:
        """Check if OpenAI service is available"""
        return self.client is not None and self.async_client is not None
    
    async def generate_workflow_with_validation(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate workflow with comprehensive validation and error handling
        
        Args:
            prompt: Natural language description of the workflow
            context: Additional context for workflow generation
            
        Returns:
            Dict containing the generated workflow and metadata
        """
        try:
            if not self.is_available():
                logger.warning("OpenAI not available, using fallback generation")
                return await self._generate_fallback_workflow(prompt, context)
            
            # Try primary generation
            result = await self._generate_workflow_primary(prompt, context)
            
            # Validate and enhance
            if self.validation_enabled:
                validated_result = await self._validate_and_enhance_workflow(result, prompt)
                return validated_result
            
            return result
            
        except Exception as e:
            logger.error(f"Error in workflow generation: {str(e)}")
            return await self._generate_fallback_workflow(prompt, context)
    
    async def _generate_workflow_primary(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Primary workflow generation using OpenAI"""
        system_prompt = self._build_advanced_system_prompt()
        user_prompt = self._build_enhanced_user_prompt(prompt, context)
        
        try:
            response = await self.async_client.chat.completions.create(
                model=getattr(settings, 'OPENAI_MODEL', 'gpt-4-turbo-preview'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=getattr(settings, 'OPENAI_MAX_TOKENS', 4000),
                response_format={"type": "json_object"}
            )
            
            workflow_data = json.loads(response.choices[0].message.content)
            
            return {
                "workflow": workflow_data,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "generation_method": "openai_primary",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Primary generation failed: {str(e)}")
            raise
    
    async def _validate_and_enhance_workflow(self, result: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Validate and enhance the generated workflow"""
        workflow = result["workflow"]
        
        # Validate structure
        validation_result = await self._validate_workflow_structure(workflow)
        
        if not validation_result["valid"]:
            logger.warning(f"Workflow validation failed: {validation_result['errors']}")
            
            # Attempt to fix validation issues
            fixed_workflow = await self._fix_workflow_issues(workflow, validation_result["errors"])
            workflow = fixed_workflow
        
        # Enhance with additional metadata
        enhanced_workflow = await self._enhance_workflow_metadata(workflow, prompt)
        
        result["workflow"] = enhanced_workflow
        result["validation"] = validation_result
        
        return result
    
    async def _validate_workflow_structure(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive workflow structure validation"""
        errors = []
        warnings = []
        
        try:
            # Check required top-level fields
            required_fields = ["name", "description", "nodes", "edges"]
            for field in required_fields:
                if field not in workflow:
                    errors.append(f"Missing required field: {field}")
            
            # Validate nodes
            nodes = workflow.get("nodes", [])
            if not isinstance(nodes, list):
                errors.append("Nodes must be a list")
            elif len(nodes) == 0:
                errors.append("Workflow must have at least one node")
            else:
                node_ids = set()
                for i, node in enumerate(nodes):
                    node_errors = self._validate_node(node, i)
                    errors.extend(node_errors)
                    
                    if "id" in node:
                        if node["id"] in node_ids:
                            errors.append(f"Duplicate node ID: {node['id']}")
                        node_ids.add(node["id"])
            
            # Validate edges
            edges = workflow.get("edges", [])
            if not isinstance(edges, list):
                errors.append("Edges must be a list")
            else:
                edge_ids = set()
                for i, edge in enumerate(edges):
                    edge_errors = self._validate_edge(edge, i, node_ids)
                    errors.extend(edge_errors)
                    
                    if "id" in edge:
                        if edge["id"] in edge_ids:
                            errors.append(f"Duplicate edge ID: {edge['id']}")
                        edge_ids.add(edge["id"])
            
            # Check workflow connectivity
            connectivity_issues = self._check_workflow_connectivity(nodes, edges)
            warnings.extend(connectivity_issues)
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": []
            }
    
    def _validate_node(self, node: Dict[str, Any], index: int) -> List[str]:
        """Validate individual node"""
        errors = []
        
        # Check required fields
        required_fields = ["id", "type", "position", "data"]
        for field in required_fields:
            if field not in node:
                errors.append(f"Node {index} missing required field: {field}")
        
        # Validate node type
        valid_types = {"trigger", "action", "connection", "condition", "data"}
        if "type" in node and node["type"] not in valid_types:
            errors.append(f"Node {index} has invalid type: {node['type']}")
        
        # Validate position
        if "position" in node:
            pos = node["position"]
            if not isinstance(pos, dict) or "x" not in pos or "y" not in pos:
                errors.append(f"Node {index} has invalid position format")
        
        # Validate data structure
        if "data" in node:
            data = node["data"]
            if not isinstance(data, dict):
                errors.append(f"Node {index} data must be a dictionary")
            elif "label" not in data:
                warnings = [f"Node {index} missing label in data"]
        
        return errors
    
    def _validate_edge(self, edge: Dict[str, Any], index: int, node_ids: set) -> List[str]:
        """Validate individual edge"""
        errors = []
        
        # Check required fields
        required_fields = ["id", "source", "target"]
        for field in required_fields:
            if field not in edge:
                errors.append(f"Edge {index} missing required field: {field}")
        
        # Validate node references
        if "source" in edge and edge["source"] not in node_ids:
            errors.append(f"Edge {index} references non-existent source: {edge['source']}")
        
        if "target" in edge and edge["target"] not in node_ids:
            errors.append(f"Edge {index} references non-existent target: {edge['target']}")
        
        return errors
    
    def _check_workflow_connectivity(self, nodes: List[Dict], edges: List[Dict]) -> List[str]:
        """Check if workflow is properly connected"""
        warnings = []
        
        if len(nodes) > 1 and len(edges) == 0:
            warnings.append("Multi-node workflow has no edges connecting nodes")
        
        # Check if all nodes are connected
        if len(nodes) > 1 and len(edges) > 0:
            connected_nodes = set()
            for edge in edges:
                if "source" in edge and "target" in edge:
                    connected_nodes.add(edge["source"])
                    connected_nodes.add(edge["target"])
            
            isolated_nodes = len(nodes) - len(connected_nodes)
            if isolated_nodes > 0:
                warnings.append(f"{isolated_nodes} nodes are not connected to the workflow")
        
        return warnings
    
    async def _fix_workflow_issues(self, workflow: Dict[str, Any], issues: List[str]) -> Dict[str, Any]:
        """Attempt to fix common workflow issues"""
        try:
            # Basic fixes for common issues
            if "name" not in workflow:
                workflow["name"] = "Generated Workflow"
            
            if "description" not in workflow:
                workflow["description"] = "Automatically generated workflow"
            
            # Ensure nodes have required structure
            nodes = workflow.get("nodes", [])
            for i, node in enumerate(nodes):
                if "id" not in node:
                    node["id"] = f"node_{i}"
                if "type" not in node:
                    node["type"] = "action"  # Default fallback
                if "position" not in node:
                    node["position"] = {"x": 100 + (i * 300), "y": 100}
                if "data" not in node:
                    node["data"] = {"label": node.get("id", f"Node {i}")}
            
            # Ensure edges have required structure
            edges = workflow.get("edges", [])
            for i, edge in enumerate(edges):
                if "id" not in edge:
                    edge["id"] = f"edge_{i}"
            
            return workflow
            
        except Exception as e:
            logger.error(f"Error fixing workflow issues: {str(e)}")
            return workflow
    
    async def _enhance_workflow_metadata(self, workflow: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Enhance workflow with additional metadata"""
        try:
            # Add generation metadata
            workflow["metadata"] = workflow.get("metadata", {})
            workflow["metadata"].update({
                "generated_at": datetime.utcnow().isoformat(),
                "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt,
                "generation_method": "enhanced_ai",
                "version": "1.0"
            })
            
            return workflow
        except Exception as e:
            logger.error(f"Error enhancing workflow metadata: {str(e)}")
            return workflow
    
    async def _generate_fallback_workflow(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate fallback workflow when OpenAI is unavailable"""
        logger.info("Using fallback workflow generation")
        
        # Simple fallback based on prompt keywords
        prompt_lower = prompt.lower()
        
        if "email" in prompt_lower and ("welcome" in prompt_lower or "signup" in prompt_lower):
            workflow = self._create_welcome_email_workflow()
        elif "api" in prompt_lower and "integration" in prompt_lower:
            workflow = self._create_api_integration_workflow()
        elif "data" in prompt_lower and "process" in prompt_lower:
            workflow = self._create_data_processing_workflow()
        else:
            workflow = self._create_generic_workflow(prompt)
        
        return {
            "workflow": workflow,
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            },
            "model": "fallback",
            "generation_method": "fallback",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _build_advanced_system_prompt(self) -> str:
        """Build advanced system prompt for workflow generation"""
        return """You are an expert AI workflow architect for the Flov7 platform. Create sophisticated, production-ready workflows using the 5-primitives system.

PRIMITIVE TYPES:
- trigger: webhook, schedule, database, manual, api, email, sms, iot
- action: ai_process, api_call, email_send, db_query, notification, transform, wait, custom
- connection: gmail, slack, hubspot, database, api, webhook, oauth, api_key
- condition: if_else, filter, switch, loop, compare, regex, json_path
- data: mapping, transform, filter, merge, split, enrich, validate

REQUIREMENTS:
1. Start with a trigger primitive
2. Ensure logical flow between primitives
3. Include proper error handling
4. Use realistic configurations
5. Return valid JSON only

JSON STRUCTURE:
{
  "name": "Workflow Name",
  "description": "Clear description",
  "nodes": [
    {
      "id": "unique_id",
      "type": "primitive_type",
      "position": {"x": 100, "y": 100},
      "data": {"label": "Label", "config": {...}}
    }
  ],
  "edges": [{"id": "edge_id", "source": "source", "target": "target"}]
}"""
    
    def _build_enhanced_user_prompt(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        """Build enhanced user prompt"""
        user_prompt = f"Create a workflow for: {prompt}\n\n"
        
        if context:
            user_context_parts = []
            for key, value in context.items():
                user_context_parts.append(f"{key}: {value}")
            
            if user_context_parts:
                user_prompt += "Context:\n" + "\n".join(user_context_parts) + "\n\n"
        
        user_prompt += "Requirements:\n- Production-ready workflow\n- Proper error handling\n- Realistic configurations\n- Complete and functional"
        
        return user_prompt
    
    def _create_welcome_email_workflow(self) -> Dict[str, Any]:
        """Create welcome email workflow template"""
        return {
            "name": "Welcome Email Workflow",
            "description": "Automatically send welcome emails to new users",
            "nodes": [
                {
                    "id": "trigger_1",
                    "type": "trigger",
                    "position": {"x": 100, "y": 100},
                    "data": {
                        "label": "User Registration",
                        "config": {"trigger_type": "webhook", "endpoint": "/api/register"}
                    }
                },
                {
                    "id": "data_1",
                    "type": "data",
                    "position": {"x": 400, "y": 100},
                    "data": {
                        "label": "Validate User Data",
                        "config": {"operation_type": "validate", "rules": {"email": "required", "name": "required"}}
                    }
                },
                {
                    "id": "action_1",
                    "type": "action",
                    "position": {"x": 700, "y": 100},
                    "data": {
                        "label": "Send Welcome Email",
                        "config": {"action_type": "email_send", "template": "welcome", "delay": 0}
                    }
                }
            ],
            "edges": [
                {"id": "edge_1", "source": "trigger_1", "target": "data_1"},
                {"id": "edge_2", "source": "data_1", "target": "action_1"}
            ]
        }
    
    def _create_api_integration_workflow(self) -> Dict[str, Any]:
        """Create API integration workflow template"""
        return {
            "name": "API Data Sync Workflow",
            "description": "Sync data from external API to database",
            "nodes": [
                {
                    "id": "trigger_1",
                    "type": "trigger",
                    "position": {"x": 100, "y": 100},
                    "data": {
                        "label": "Schedule Trigger",
                        "config": {"trigger_type": "schedule", "cron": "0 */6 * * *"}
                    }
                },
                {
                    "id": "connection_1",
                    "type": "connection",
                    "position": {"x": 400, "y": 100},
                    "data": {
                        "label": "API Connection",
                        "config": {"connection_type": "api", "base_url": "https://api.example.com"}
                    }
                },
                {
                    "id": "action_1",
                    "type": "action",
                    "position": {"x": 700, "y": 100},
                    "data": {
                        "label": "Fetch Data",
                        "config": {"action_type": "api_call", "endpoint": "/data", "method": "GET"}
                    }
                },
                {
                    "id": "data_1",
                    "type": "data",
                    "position": {"x": 1000, "y": 100},
                    "data": {
                        "label": "Store Data",
                        "config": {"operation_type": "transform", "store_in": "database"}
                    }
                }
            ],
            "edges": [
                {"id": "edge_1", "source": "trigger_1", "target": "connection_1"},
                {"id": "edge_2", "source": "connection_1", "target": "action_1"},
                {"id": "edge_3", "source": "action_1", "target": "data_1"}
            ]
        }
    
    def _create_data_processing_workflow(self) -> Dict[str, Any]:
        """Create data processing workflow template"""
        return {
            "name": "Data Processing Pipeline",
            "description": "Process incoming data with validation and transformation",
            "nodes": [
                {
                    "id": "trigger_1",
                    "type": "trigger",
                    "position": {"x": 100, "y": 100},
                    "data": {
                        "label": "Data Upload",
                        "config": {"trigger_type": "webhook", "endpoint": "/upload"}
                    }
                },
                {
                    "id": "data_1",
                    "type": "data",
                    "position": {"x": 400, "y": 100},
                    "data": {
                        "label": "Validate Data",
                        "config": {"operation_type": "validate", "schema": "user_schema"}
                    }
                },
                {
                    "id": "condition_1",
                    "type": "condition",
                    "position": {"x": 700, "y": 100},
                    "data": {
                        "label": "Check Validity",
                        "config": {"condition_type": "if_else", "condition": "data.valid == true"}
                    }
                },
                {
                    "id": "data_2",
                    "type": "data",
                    "position": {"x": 1000, "y": 50},
                    "data": {
                        "label": "Process Valid Data",
                        "config": {"operation_type": "transform", "transform_type": "normalize"}
                    }
                },
                {
                    "id": "action_1",
                    "type": "action",
                    "position": {"x": 1000, "y": 150},
                    "data": {
                        "label": "Handle Invalid Data",
                        "config": {"action_type": "notification", "type": "error_alert"}
                    }
                }
            ],
            "edges": [
                {"id": "edge_1", "source": "trigger_1", "target": "data_1"},
                {"id": "edge_2", "source": "data_1", "target": "condition_1"},
                {"id": "edge_3", "source": "condition_1", "target": "data_2"},
                {"id": "edge_4", "source": "condition_1", "target": "action_1"}
            ]
        }
    
    def _create_generic_workflow(self, prompt: str) -> Dict[str, Any]:
        """Create generic workflow based on prompt"""
        return {
            "name": f"Workflow for: {prompt[:50]}...",
            "description": f"Generated workflow for: {prompt}",
            "nodes": [
                {
                    "id": "trigger_1",
                    "type": "trigger",
                    "position": {"x": 100, "y": 100},
                    "data": {
                        "label": "Start Trigger",
                        "config": {"trigger_type": "manual"}
                    }
                },
                {
                    "id": "action_1",
                    "type": "action",
                    "position": {"x": 400, "y": 100},
                    "data": {
                        "label": "Process Action",
                        "config": {"action_type": "custom", "description": prompt}
                    }
                }
            ],
            "edges": [
                {"id": "edge_1", "source": "trigger_1", "target": "action_1"}
            ]
        }


# Global enhanced client instance
enhanced_openai_client = EnhancedOpenAIClient()
