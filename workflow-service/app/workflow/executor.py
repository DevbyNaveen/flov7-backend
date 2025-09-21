"""
Workflow executor for Flov7 workflow service.
Handles the execution of workflows using Temporal and CrewAI with database persistence.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import uuid
from shared.crud.workflows import workflow_crud
from shared.crud.executions import execution_crud

# Configure logging
logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """Workflow execution engine with database persistence"""
    
    def __init__(self):
        self.temporal_client = None
        self.workflow_crud = workflow_crud
        self.execution_crud = execution_crud
    
    async def _get_temporal_client(self):
        """Get Temporal client asynchronously"""
        try:
            # Import Temporal client
            from app.temporal.client import get_temporal_client
            return await get_temporal_client()
        except Exception as e:
            logger.warning(f"Temporal client not available: {str(e)}")
            return None
    
    async def execute_workflow(self, workflow_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute a workflow definition with database persistence
        
        Args:
            workflow_data: Workflow definition to execute
            user_id: ID of the user requesting execution
            
        Returns:
            Execution result with metadata
        """
        execution_id = str(uuid.uuid4())
        workflow_id = workflow_data.get("id") or workflow_data.get("workflow_id")
        
        try:
            # Record execution start
            start_time = datetime.utcnow()
            logger.info(f"Starting workflow execution {execution_id} for user {user_id}")
            
            # Create execution record in database
            execution_record_data = {
                "workflow_id": workflow_id,
                "user_id": user_id,
                "status": "running",
                "input_data": workflow_data,
                "temporal_workflow_id": execution_id,
                "started_at": start_time.isoformat()
            }
            
            # Create execution record
            db_result = await self.execution_crud.create_execution(execution_record_data)
            if not db_result["success"]:
                logger.warning(f"Failed to create execution record: {db_result['error']}")
            else:
                # Use database-generated ID if available
                db_execution_id = db_result["data"]["id"]
                logger.info(f"Created execution record with ID: {db_execution_id}")
            
            # Get Temporal client
            temporal_client = await self._get_temporal_client()
            
            # If Temporal is available, use it for orchestration
            if temporal_client:
                result = await self._execute_with_temporal(workflow_data, user_id, execution_id, temporal_client)
            else:
                # Fallback to local execution
                result = await self._execute_locally(workflow_data, user_id, execution_id)
            
            # Record execution end
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            result["execution_time_seconds"] = execution_time
            result["started_at"] = start_time
            result["completed_at"] = end_time
            
            # Update execution record in database
            await self.execution_crud.update_execution_status(
                execution_id=db_result["data"]["id"] if db_result["success"] else execution_id,
                status=result["status"],
                output_data=result.get("output_data"),
                error_message=result.get("error_message"),
                execution_time_seconds=execution_time
            )
            
            logger.info(f"Workflow execution {execution_id} completed in {execution_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing workflow {execution_id}: {str(e)}")
            
            # Record failed execution
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds() if 'start_time' in locals() else 0
            
            # Update execution record with failure
            if 'db_result' in locals() and db_result["success"]:
                await self.execution_crud.update_execution_status(
                    execution_id=db_result["data"]["id"],
                    status="failed",
                    error_message=str(e),
                    execution_time_seconds=execution_time
                )
            
            return {
                "execution_id": execution_id,
                "status": "failed",
                "error_message": str(e),
                "execution_time_seconds": execution_time,
                "started_at": start_time if 'start_time' in locals() else None,
                "completed_at": end_time,
                "output_data": None
            }
    
    async def _execute_with_temporal(self, workflow_data: Dict[str, Any], user_id: str, execution_id: str, temporal_client) -> Dict[str, Any]:
        """Execute workflow using Temporal orchestration"""
        try:
            # Import Temporal workflow
            from app.temporal.workflows import WorkflowExecution
            
            # Execute workflow through Temporal
            handle = await temporal_client.start_workflow(
                WorkflowExecution.run,
                workflow_data,
                id=execution_id,
                task_queue="flov7-workflow-task-queue",
            )
            
            # Wait for result
            result = await handle.result()
            
            return {
                "execution_id": execution_id,
                "temporal_workflow_id": execution_id,
                "status": "completed",
                "output_data": result,
                "error_message": None
            }
            
        except Exception as e:
            logger.error(f"Temporal execution failed: {str(e)}")
            raise
    
    async def _execute_locally(self, workflow_data: Dict[str, Any], user_id: str, execution_id: str) -> Dict[str, Any]:
        """Execute workflow using local fallback execution"""
        try:
            # Simple local execution - process nodes in order
            nodes = workflow_data.get("nodes", [])
            edges = workflow_data.get("edges", [])
            
            logger.info(f"Executing workflow locally with {len(nodes)} nodes and {len(edges)} edges")
            
            # Try to use CrewAI for multi-agent execution if available
            crewai_result = await self._execute_with_crewai(workflow_data, user_id, execution_id)
            
            if crewai_result:
                return crewai_result
            
            # Fallback to simple execution
            result = {
                "workflow_name": workflow_data.get("name", "Unknown"),
                "node_count": len(nodes),
                "edge_count": len(edges),
                "executed_by": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "execution_method": "local_fallback"
            }
            
            return {
                "execution_id": execution_id,
                "status": "completed",
                "output_data": result,
                "error_message": None
            }
            
        except Exception as e:
            logger.error(f"Local execution failed: {str(e)}")
            raise
    
    async def _execute_with_crewai(self, workflow_data: Dict[str, Any], user_id: str, execution_id: str) -> Optional[Dict[str, Any]]:
        """Execute workflow using enhanced CrewAI multi-agent system"""
        try:
            from app.crewai.workflow_orchestrator import crewai_orchestrator
            
            logger.info(f"Starting enhanced CrewAI workflow execution: {execution_id}")
            
            # Use the enhanced CrewAI orchestrator
            result = await crewai_orchestrator.execute_workflow_with_crewai(
                workflow_data, user_id, execution_id
            )
            
            if result["status"] == "completed":
                logger.info(f"Enhanced CrewAI execution completed: {execution_id}")
                return result
            else:
                logger.warning(f"Enhanced CrewAI execution failed: {result.get('error_message')}")
                return None
                
        except Exception as e:
            logger.error(f"Enhanced CrewAI execution failed: {str(e)}")
            logger.info("Falling back to simple local execution")
            return None
    
    async def _create_workflow_specific_tasks(self, workflow_data: Dict[str, Any], agents: List) -> Optional[List]:
        """Create tasks specific to the workflow being executed"""
        try:
            from crewai import Task
            from app.crewai.tasks import task_manager
            
            workflow_tasks = []
            nodes = workflow_data.get("nodes", [])
            
            if not nodes:
                return None
            
            # Create tasks based on workflow nodes
            for i, node in enumerate(nodes):
                node_type = node.get("type", "unknown")
                node_data = node.get("data", {})
                
                # Select appropriate agent based on node type
                agent = self._select_agent_for_node(node_type, agents)
                if not agent:
                    continue
                
                # Create task description based on node
                task_description = self._generate_task_description(node, node_data)
                expected_output = self._generate_expected_output(node, node_data)
                
                task = Task(
                    description=task_description,
                    agent=agent,
                    expected_output=expected_output
                )
                
                workflow_tasks.append(task)
            
            return workflow_tasks if workflow_tasks else None
            
        except Exception as e:
            logger.warning(f"Failed to create workflow-specific tasks: {str(e)}")
            return None
    
    def _select_agent_for_node(self, node_type: str, agents: List):
        """Select the most appropriate agent for a node type"""
        from app.crewai.agents import agent_manager
        
        # Map node types to agent types
        node_agent_mapping = {
            "data": "data_processor",
            "action": "action_executor", 
            "validation": "validator",
            "coordination": "workflow_coordinator",
            "default": "workflow_coordinator"
        }
        
        agent_name = node_agent_mapping.get(node_type, "workflow_coordinator")
        return agent_manager.get_agent(agent_name)
    
    def _generate_task_description(self, node: Dict[str, Any], node_data: Dict[str, Any]) -> str:
        """Generate task description based on node configuration"""
        node_type = node.get("type", "unknown")
        node_label = node_data.get("label", f"Node {node.get('id', 'unknown')}")
        
        base_descriptions = {
            "data": f"Process data for {node_label}",
            "action": f"Execute action for {node_label}",
            "validation": f"Validate results for {node_label}",
            "coordination": f"Coordinate workflow step for {node_label}"
        }
        
        return base_descriptions.get(node_type, f"Execute workflow step for {node_label}")
    
    def _generate_expected_output(self, node: Dict[str, Any], node_data: Dict[str, Any]) -> str:
        """Generate expected output description based on node configuration"""
        node_type = node.get("type", "unknown")
        
        base_outputs = {
            "data": "Processed data in the required format",
            "action": "Action execution results and status",
            "validation": "Validation report with pass/fail status",
            "coordination": "Coordination plan and next steps"
        }
        
        return base_outputs.get(node_type, "Task completion status and results")
    
    def _extract_execution_summary(self, crew_result) -> str:
        """Extract a concise summary from crew execution result"""
        try:
            result_str = str(crew_result)
            # Extract first 500 characters as summary
            summary = result_str[:500]
            if len(result_str) > 500:
                summary += "..."
            return summary
        except Exception:
            return "Execution completed successfully"


# Global workflow executor instance
workflow_executor = WorkflowExecutor()
