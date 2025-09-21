"""
Temporal activities for Flov7 workflow service.
Defines activities for executing workflow nodes and handling workflow operations.
"""

from temporalio import activity
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import asyncio
from shared.crud.workflows import workflow_crud
from shared.crud.executions import execution_crud

# Configure logging
logger = logging.getLogger(__name__)


class WorkflowActivities:
    """Activities for workflow execution and management"""
    
    @activity.defn
    async def execute_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single workflow node
        
        Args:
            node_data: Node configuration and input data
            
        Returns:
            Node execution result
        """
        try:
            node_id = node_data.get("id", "unknown")
            node_type = node_data.get("type", "unknown")
            node_name = node_data.get("data", {}).get("name", node_id)
            
            logger.info(f"Executing node {node_id} of type {node_type}")
            
            # Get node configuration
            config = node_data.get("data", {})
            inputs = node_data.get("inputs", {})
            
            # Execute based on node type
            if node_type == "api_call":
                result = await self._execute_api_call(config, inputs)
            elif node_type == "condition":
                result = await self._execute_condition(config, inputs)
            elif node_type == "transform":
                result = await self._execute_transform(config, inputs)
            elif node_type == "delay":
                result = await self._execute_delay(config, inputs)
            elif node_type == "database":
                result = await self._execute_database_operation(config, inputs)
            elif node_type == "webhook":
                result = await self._execute_webhook(config, inputs)
            elif node_type == "ai_agent":
                result = await self._execute_ai_agent(config, inputs)
            else:
                # Generic execution for unknown types
                result = {
                    "status": "completed",
                    "output": inputs,
                    "message": f"Executed generic node: {node_name}"
                }
            
            return {
                "node_id": node_id,
                "node_type": node_type,
                "status": "completed",
                "output": result,
                "timestamp": datetime.utcnow().isoformat(),
                "execution_duration_ms": activity.info().current_attempt_scheduled_time
            }
            
        except Exception as e:
            logger.error(f"Failed to execute node {node_data.get('id', 'unknown')}: {str(e)}")
            raise activity.ApplicationError(f"Node execution failed: {str(e)}")
    
    @activity.defn
    async def validate_workflow_structure(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate workflow structure and dependencies
        
        Args:
            workflow_data: Complete workflow definition
            
        Returns:
            Validation result with issues and recommendations
        """
        try:
            workflow_id = workflow_data.get("id", "unknown")
            nodes = workflow_data.get("nodes", [])
            edges = workflow_data.get("edges", [])
            
            logger.info(f"Validating workflow structure: {workflow_id}")
            
            validation_result = {
                "valid": True,
                "issues": [],
                "warnings": [],
                "recommendations": []
            }
            
            # Validate nodes
            if not nodes:
                validation_result["valid"] = False
                validation_result["issues"].append("Workflow has no nodes")
            
            # Validate edges
            node_ids = {node.get("id") for node in nodes}
            for edge in edges:
                source = edge.get("source")
                target = edge.get("target")
                
                if source not in node_ids:
                    validation_result["issues"].append(f"Edge references non-existent source: {source}")
                    validation_result["valid"] = False
                
                if target not in node_ids:
                    validation_result["issues"].append(f"Edge references non-existent target: {target}")
                    validation_result["valid"] = False
            
            # Check for cycles
            if self._has_cycles(nodes, edges):
                validation_result["issues"].append("Workflow contains cycles")
                validation_result["valid"] = False
            
            # Check for disconnected nodes
            connected_nodes = set()
            for edge in edges:
                connected_nodes.add(edge.get("source"))
                connected_nodes.add(edge.get("target"))
            
            disconnected = node_ids - connected_nodes
            if disconnected and len(nodes) > 1:
                validation_result["warnings"].append(f"Disconnected nodes: {list(disconnected)}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Workflow validation failed: {str(e)}")
            raise activity.ApplicationError(f"Validation failed: {str(e)}")
    
    @activity.defn
    async def update_execution_status(self, execution_id: str, status: str, result_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update execution status in database
        
        Args:
            execution_id: Execution ID
            status: New status
            result_data: Optional result data
            
        Returns:
            Update result
        """
        try:
            logger.info(f"Updating execution {execution_id} status to {status}")
            
            update_data = {"status": status}
            if result_data:
                update_data["output_data"] = result_data
            
            result = await execution_crud.update_execution_status(
                execution_id=execution_id,
                **update_data
            )
            
            return {
                "success": result.get("success", False),
                "message": f"Updated execution {execution_id} to {status}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update execution status: {str(e)}")
            raise activity.ApplicationError(f"Status update failed: {str(e)}")
    
    @activity.defn
    async def log_workflow_event(self, execution_id: str, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log workflow execution event
        
        Args:
            execution_id: Execution ID
            event_type: Type of event
            event_data: Event details
            
        Returns:
            Log result
        """
        try:
            logger.info(f"Logging event {event_type} for execution {execution_id}")
            
            # In a real implementation, this would write to a dedicated events table
            log_entry = {
                "execution_id": execution_id,
                "event_type": event_type,
                "event_data": event_data,
                "timestamp": datetime.utcnow().isoformat(),
                "activity_info": {
                    "activity_id": activity.info().activity_id,
                    "attempt": activity.info().attempt
                }
            }
            
            logger.info(f"Workflow event logged: {log_entry}")
            
            return {
                "logged": True,
                "event_id": str(activity.info().activity_id),
                "timestamp": log_entry["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Failed to log workflow event: {str(e)}")
            raise activity.ApplicationError(f"Event logging failed: {str(e)}")
    
    # Private helper methods for node execution
    
    async def _execute_api_call(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API call node"""
        import httpx
        
        url = config.get("url")
        method = config.get("method", "GET").upper()
        headers = config.get("headers", {})
        body = inputs.get("body", config.get("body", {}))
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers, params=inputs)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=body)
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=body)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.json() if response.content else None,
                "success": 200 <= response.status_code < 300
            }
    
    async def _execute_condition(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute condition node"""
        condition = config.get("condition", "")
        
        # Simple condition evaluation (in production, use a proper expression engine)
        try:
            # Create a safe evaluation environment
            eval_locals = {"inputs": inputs, **inputs}
            result = eval(condition, {"__builtins__": {}}, eval_locals)
            
            return {
                "condition": condition,
                "result": bool(result),
                "branch": "true" if result else "false"
            }
        except Exception as e:
            return {
                "condition": condition,
                "result": False,
                "error": str(e),
                "branch": "error"
            }
    
    async def _execute_transform(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute transform node"""
        transform_type = config.get("transform_type", "mapping")
        
        if transform_type == "mapping":
            mapping = config.get("mapping", {})
            output = {}
            
            for key, value_expr in mapping.items():
                try:
                    # Simple expression evaluation
                    eval_locals = {"inputs": inputs, **inputs}
                    output[key] = eval(value_expr, {"__builtins__": {}}, eval_locals)
                except Exception as e:
                    output[key] = f"Error: {str(e)}"
            
            return {"transformed_data": output}
        
        return {"transformed_data": inputs}
    
    async def _execute_delay(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute delay node"""
        delay_seconds = config.get("delay_seconds", 1)
        await asyncio.sleep(delay_seconds)
        return {"delayed": True, "delay_seconds": delay_seconds}
    
    async def _execute_database_operation(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database operation node"""
        operation = config.get("operation", "select")
        table = config.get("table")
        
        # In a real implementation, this would use the database client
        return {
            "operation": operation,
            "table": table,
            "affected_rows": 1,
            "result": {"id": 1, "data": "mock_result"}
        }
    
    async def _execute_webhook(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute webhook node"""
        url = config.get("url")
        method = config.get("method", "POST")
        
        # In a real implementation, this would make the webhook call
        return {
            "webhook_url": url,
            "method": method,
            "status": "delivered",
            "response_time_ms": 150
        }
    
    async def _execute_ai_agent(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute AI agent node using CrewAI orchestrator"""
        agent_type = config.get("agent_type", "generic")
        prompt = config.get("prompt", "")
        
        try:
            # Import CrewAI orchestrator for AI task execution
            from app.crewai.workflow_orchestrator import crewai_orchestrator
            
            # Create focused AI task using CrewAI
            ai_task_config = {
                "type": "ai_agent",
                "agent_type": agent_type,
                "prompt": prompt,
                "context": inputs
            }
            
            # Execute with CrewAI orchestrator
            crewai_result = await crewai_orchestrator.execute_ai_task(
                ai_task_config, 
                context=inputs
            )
            
            return {
                "agent_type": agent_type,
                "prompt": prompt,
                "response": crewai_result.get("response", "Task completed"),
                "confidence": crewai_result.get("confidence", 0.85),
                "crewai_execution": True,
                "metadata": crewai_result.get("metadata", {})
            }
            
        except Exception as e:
            logger.warning(f"CrewAI execution failed, falling back to direct processing: {str(e)}")
            
            # Fallback to basic AI processing
            return {
                "agent_type": agent_type,
                "prompt": prompt,
                "response": f"AI agent processed: {prompt}",
                "confidence": 0.75,
                "crewai_execution": False,
                "error": str(e),
                "fallback": True
            }
    
    def _has_cycles(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> bool:
        """Check if workflow has cycles using DFS"""
        if not nodes or not edges:
            return False
        
        # Build adjacency list
        graph = {}
        node_ids = {node.get("id") for node in nodes}
        
        for node_id in node_ids:
            graph[node_id] = []
        
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            if source in graph and target in graph:
                graph[source].append(target)
        
        # DFS cycle detection
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if dfs(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node_id in node_ids:
            if node_id not in visited:
                if dfs(node_id):
                    return True
        
        return False


# Create activity instance for registration
workflow_activities = WorkflowActivities()
