"""
Temporal workflows for Flov7 workflow service.
Defines Temporal workflow definitions for orchestration with proper activity integration.
"""

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError, ApplicationError
from typing import Dict, Any, Optional, List
from datetime import timedelta
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Import activities
with workflow.unsafe.imports_passed_through():
    from app.temporal.activities import workflow_activities


@workflow.defn
class WorkflowExecution:
    """Temporal workflow definition for executing Flov7 workflows with proper orchestration"""
    
    def __init__(self):
        self.execution_results = {}
        self.execution_logs = []
    
    @workflow.run
    async def run(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the workflow execution with proper orchestration
        
        Args:
            workflow_data: Workflow definition to execute
            
        Returns:
            Complete execution result with node outputs and metadata
        """
        try:
            workflow_name = workflow_data.get("name", "Unknown")
            workflow_id = workflow_data.get("id", "unknown")
            
            logger.info(f"Starting Temporal workflow execution: {workflow_name}")
            
            # Log workflow start
            await workflow.execute_activity(
                workflow_activities.log_workflow_event,
                workflow_id,
                "workflow_started",
                {"workflow_name": workflow_name, "node_count": len(workflow_data.get("nodes", []))},
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )
            
            # Validate workflow structure first
            validation_result = await workflow.execute_activity(
                workflow_activities.validate_workflow_structure,
                workflow_data,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=2)
            )
            
            if not validation_result["valid"]:
                raise ApplicationError(f"Workflow validation failed: {validation_result['issues']}")
            
            # Process workflow nodes with proper orchestration
            result = await self._execute_workflow_graph(workflow_data)
            
            # Log workflow completion
            await workflow.execute_activity(
                workflow_activities.log_workflow_event,
                workflow_id,
                "workflow_completed",
                {"result": result},
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )
            
            logger.info(f"Completed Temporal workflow execution: {workflow_name}")
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            
            # Log workflow failure
            try:
                await workflow.execute_activity(
                    workflow_activities.log_workflow_event,
                    workflow_data.get("id", "unknown"),
                    "workflow_failed",
                    {"error": str(e)},
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=RetryPolicy(maximum_attempts=2)
                )
            except Exception as log_error:
                logger.warning(f"Failed to log workflow failure: {str(log_error)}")
            
            raise
    
    async def _execute_workflow_graph(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute workflow graph with proper dependency resolution
        
        Args:
            workflow_data: Complete workflow definition
            
        Returns:
            Complete execution result with all node outputs
        """
        nodes = workflow_data.get("nodes", [])
        edges = workflow_data.get("edges", [])
        workflow_id = workflow_data.get("id", "unknown")
        
        if not nodes:
            return {
                "workflow_name": workflow_data.get("name", "Unknown"),
                "status": "completed",
                "node_results": {},
                "execution_path": [],
                "total_nodes": 0,
                "timestamp": workflow.now().isoformat()
            }
        
        # Build execution graph
        execution_order = self._build_execution_order(nodes, edges)
        
        # Execute nodes in dependency order
        node_results = {}
        execution_path = []
        
        for node_id in execution_order:
            node = next(n for n in nodes if n["id"] == node_id)
            
            # Prepare inputs based on dependencies
            node_inputs = self._prepare_node_inputs(node, edges, node_results)
            
            # Execute node
            node_data = {
                "id": node_id,
                "type": node.get("type", "unknown"),
                "data": node.get("data", {}),
                "inputs": node_inputs
            }
            
            try:
                result = await workflow.execute_activity(
                    workflow_activities.execute_node,
                    node_data,
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=RetryPolicy(
                        maximum_attempts=3,
                        initial_interval=timedelta(seconds=1),
                        maximum_interval=timedelta(seconds=10),
                        backoff_coefficient=2.0
                    )
                )
                
                node_results[node_id] = result
                execution_path.append(node_id)
                
                # Update execution status
                await workflow.execute_activity(
                    workflow_activities.update_execution_status,
                    workflow_id,
                    "running",
                    {"current_node": node_id, "completed_nodes": list(node_results.keys())},
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=RetryPolicy(maximum_attempts=2)
                )
                
            except ActivityError as e:
                logger.error(f"Node {node_id} execution failed: {str(e)}")
                node_results[node_id] = {
                    "node_id": node_id,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": workflow.now().isoformat()
                }
                
                # Stop execution on failure (could be configurable)
                break
        
        return {
            "workflow_name": workflow_data.get("name", "Unknown"),
            "workflow_id": workflow_id,
            "status": "completed" if all(r.get("status") == "completed" for r in node_results.values()) else "failed",
            "node_results": node_results,
            "execution_path": execution_path,
            "total_nodes": len(nodes),
            "completed_nodes": len([r for r in node_results.values() if r.get("status") == "completed"]),
            "failed_nodes": len([r for r in node_results.values() if r.get("status") == "failed"]),
            "timestamp": workflow.now().isoformat()
        }
    
    def _build_execution_order(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[str]:
        """
        Build execution order based on dependencies using topological sort
        
        Args:
            nodes: List of workflow nodes
            edges: List of workflow edges
            
        Returns:
            Ordered list of node IDs for execution
        """
        if not edges:
            return [node["id"] for node in nodes]
        
        # Build adjacency list and in-degree count
        graph = {}
        in_degree = {}
        node_ids = {node["id"] for node in nodes}
        
        for node_id in node_ids:
            graph[node_id] = []
            in_degree[node_id] = 0
        
        # Build graph from edges
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            if source in graph and target in graph:
                graph[source].append(target)
                in_degree[target] += 1
        
        # Topological sort using Kahn's algorithm
        queue = [node_id for node_id in node_ids if in_degree[node_id] == 0]
        execution_order = []
        
        while queue:
            current = queue.pop(0)
            execution_order.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Handle cycles - nodes with remaining in-degree
        remaining_nodes = [node_id for node_id in node_ids if in_degree[node_id] > 0]
        execution_order.extend(remaining_nodes)
        
        return execution_order
    
    def _prepare_node_inputs(self, node: Dict[str, Any], edges: List[Dict[str, Any]], node_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare inputs for a node based on dependencies
        
        Args:
            node: The node to prepare inputs for
            edges: Workflow edges
            node_results: Results from previously executed nodes
            
        Returns:
            Prepared inputs for the node
        """
        node_id = node["id"]
        inputs = {}
        
        # Collect inputs from connected nodes
        for edge in edges:
            if edge.get("target") == node_id:
                source_id = edge.get("source")
                if source_id in node_results:
                    # Merge outputs from source nodes
                    source_output = node_results[source_id].get("output", {})
                    if isinstance(source_output, dict):
                        inputs.update(source_output)
        
        # Add node's own configuration data
        node_data = node.get("data", {})
        inputs.update(node_data)
        
        return inputs
    
    @workflow.signal
    async def cancel_workflow(self) -> None:
        """Signal to cancel workflow execution"""
        logger.info("Received cancel signal for workflow")
        workflow.logger.info("Workflow cancellation requested")
    
    @workflow.query
    async def get_status(self) -> str:
        """Query workflow execution status"""
        return "running"


@workflow.defn
class WorkflowValidation:
    """Temporal workflow definition for validating Flov7 workflows"""
    
    @workflow.run
    async def run(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the workflow validation using actual validation activities
        
        Args:
            workflow_data: Workflow definition to validate
            
        Returns:
            Complete validation result with issues and recommendations
        """
        try:
            workflow_name = workflow_data.get("name", "Unknown")
            logger.info(f"Starting Temporal workflow validation: {workflow_name}")
            
            # Use the validation activity
            validation_result = await workflow.execute_activity(
                workflow_activities.validate_workflow_structure,
                workflow_data,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=1),
                    backoff_coefficient=1.5
                )
            )
            
            # Add workflow metadata
            validation_result.update({
                "workflow_name": workflow_name,
                "workflow_id": workflow_data.get("id", "unknown"),
                "timestamp": workflow.now().isoformat(),
                "validation_type": "temporal_workflow_validation"
            })
            
            logger.info(f"Completed Temporal workflow validation: {workflow_name}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Workflow validation failed: {str(e)}")
            
            # Return structured error response
            return {
                "workflow_name": workflow_data.get("name", "Unknown"),
                "valid": False,
                "issues": [f"Validation error: {str(e)}"],
                "warnings": [],
                "recommendations": ["Please check workflow structure and try again"],
                "timestamp": workflow.now().isoformat(),
                "error": str(e)
            }
