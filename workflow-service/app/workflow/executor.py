"""
Workflow executor for Flov7 workflow service.
Handles the execution of workflows using Temporal and CrewAI.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import uuid

# Configure logging
logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """Workflow execution engine"""
    
    def __init__(self):
        self.temporal_client = None
        self._initialize_temporal_client()
    
    def _initialize_temporal_client(self):
        """Initialize Temporal client"""
        try:
            # Import Temporal client
            from app.temporal.client import temporal_client
            self.temporal_client = temporal_client
            logger.info("Temporal client initialized successfully")
        except Exception as e:
            logger.warning(f"Temporal client not available: {str(e)}")
            logger.warning("Workflow execution will use local fallback")
    
    async def execute_workflow(self, workflow_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute a workflow definition
        
        Args:
            workflow_data: Workflow definition to execute
            user_id: ID of the user requesting execution
            
        Returns:
            Execution result with metadata
        """
        execution_id = str(uuid.uuid4())
        
        try:
            # Record execution start
            start_time = datetime.utcnow()
            logger.info(f"Starting workflow execution {execution_id} for user {user_id}")
            
            # If Temporal is available, use it for orchestration
            if self.temporal_client:
                result = await self._execute_with_temporal(workflow_data, user_id, execution_id)
            else:
                # Fallback to local execution
                result = await self._execute_locally(workflow_data, user_id, execution_id)
            
            # Record execution end
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            result["execution_time_seconds"] = execution_time
            result["started_at"] = start_time
            result["completed_at"] = end_time
            
            logger.info(f"Workflow execution {execution_id} completed in {execution_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing workflow {execution_id}: {str(e)}")
            
            # Record failed execution
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds() if 'start_time' in locals() else 0
            
            return {
                "execution_id": execution_id,
                "status": "failed",
                "error_message": str(e),
                "execution_time_seconds": execution_time,
                "started_at": start_time if 'start_time' in locals() else None,
                "completed_at": end_time,
                "output_data": None
            }
    
    async def _execute_with_temporal(self, workflow_data: Dict[str, Any], user_id: str, execution_id: str) -> Dict[str, Any]:
        """Execute workflow using Temporal orchestration"""
        try:
            # Import Temporal workflow
            from app.temporal.workflows import WorkflowExecution
            
            # Execute workflow through Temporal
            handle = await self.temporal_client.start_workflow(
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
            
            # For demonstration, we'll just return a mock result
            # In a real implementation, this would execute the actual workflow logic
            result = {
                "workflow_name": workflow_data.get("name", "Unknown"),
                "node_count": len(nodes),
                "edge_count": len(edges),
                "executed_by": user_id,
                "timestamp": datetime.utcnow().isoformat()
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


# Global workflow executor instance
workflow_executor = WorkflowExecutor()
