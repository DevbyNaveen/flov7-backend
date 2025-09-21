"""
Workflow status tracking for Flov7 workflow service.
Handles monitoring and status updates for workflow executions with database persistence.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from shared.constants.status import EXECUTION_STATUSES, EXECUTION_STATUS_COMPLETED, EXECUTION_STATUS_FAILED
from shared.crud.executions import execution_crud
import logging

# Configure logging
logger = logging.getLogger(__name__)


class WorkflowStatusTracker:
    """Database-backed workflow execution status tracker"""
    
    def __init__(self):
        self.execution_crud = execution_crud
    
    async def create_execution_record(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new execution record in the database
        
        Args:
            execution_data: Execution data including workflow_id, user_id, etc.
            
        Returns:
            Result dictionary with success status and data
        """
        try:
            result = await self.execution_crud.create_execution(execution_data)
            if result["success"]:
                logger.info(f"Created execution record: {result['data']['id']}")
            else:
                logger.error(f"Failed to create execution record: {result['error']}")
            return result
        except Exception as e:
            logger.error(f"Error creating execution record: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_status(
        self, 
        execution_id: str, 
        status: str, 
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        execution_time_seconds: Optional[float] = None,
        cost_usd: Optional[float] = None
    ) -> bool:
        """
        Update the status of a workflow execution in the database
        
        Args:
            execution_id: ID of the workflow execution
            status: New status value
            output_data: Optional output data from execution
            error_message: Optional error message if execution failed
            execution_time_seconds: Optional execution time in seconds
            cost_usd: Optional cost in USD
            
        Returns:
            Boolean indicating success
        """
        if status not in EXECUTION_STATUSES:
            logger.warning(f"Invalid status '{status}' for execution {execution_id}")
            return False
        
        try:
            result = await self.execution_crud.update_execution_status(
                execution_id=execution_id,
                status=status,
                output_data=output_data,
                error_message=error_message,
                execution_time_seconds=execution_time_seconds,
                cost_usd=cost_usd
            )
            
            if result["success"]:
                logger.info(f"Updated status for execution {execution_id} to {status}")
                return True
            else:
                logger.error(f"Failed to update status for execution {execution_id}: {result['error']}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating status for execution {execution_id}: {str(e)}")
            return False
    
    async def get_status(self, execution_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a workflow execution from the database
        
        Args:
            execution_id: ID of the workflow execution
            user_id: ID of the user (for security)
            
        Returns:
            Status information or None if not found
        """
        try:
            result = await self.execution_crud.get_execution(execution_id, user_id)
            if result["success"]:
                execution_data = result["data"]
                return {
                    "status": execution_data["status"],
                    "updated_at": datetime.fromisoformat(execution_data["updated_at"]) if execution_data.get("updated_at") else datetime.fromisoformat(execution_data["created_at"]),
                    "metadata": {
                        "workflow_id": execution_data["workflow_id"],
                        "output_data": execution_data.get("output_data"),
                        "error_message": execution_data.get("error_message"),
                        "execution_time_seconds": execution_data.get("execution_time_seconds"),
                        "started_at": execution_data.get("started_at"),
                        "completed_at": execution_data.get("completed_at")
                    }
                }
            return None
        except Exception as e:
            logger.error(f"Error getting status for execution {execution_id}: {str(e)}")
            return None
    
    async def get_all_statuses(self, user_id: str, skip: int = 0, limit: int = 50) -> Dict[str, Any]:
        """
        Get all workflow execution statuses for a user
        
        Args:
            user_id: ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Dictionary of execution statuses with pagination info
        """
        try:
            result = await self.execution_crud.list_executions(
                user_id=user_id,
                skip=skip,
                limit=limit
            )
            return result
        except Exception as e:
            logger.error(f"Error getting all statuses for user {user_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def is_execution_completed(self, execution_id: str, user_id: str) -> bool:
        """
        Check if a workflow execution is completed
        
        Args:
            execution_id: ID of the workflow execution
            user_id: ID of the user (for security)
            
        Returns:
            Boolean indicating if execution is completed
        """
        status_info = await self.get_status(execution_id, user_id)
        if not status_info:
            return False
        
        return status_info["status"] in [EXECUTION_STATUS_COMPLETED, EXECUTION_STATUS_FAILED]
    
    async def get_execution_history(self, execution_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Get execution history for a workflow
        
        Args:
            execution_id: ID of the workflow execution
            user_id: ID of the user (for security)
            
        Returns:
            List of status updates in chronological order
        """
        try:
            # Get the execution record
            result = await self.execution_crud.get_execution(execution_id, user_id)
            if not result["success"]:
                return []
            
            execution_data = result["data"]
            
            # Build history from execution data
            history = []
            
            # Add creation event
            history.append({
                "execution_id": execution_id,
                "status": "pending",
                "timestamp": datetime.fromisoformat(execution_data["created_at"]),
                "metadata": {"event": "execution_created"}
            })
            
            # Add start event if started
            if execution_data.get("started_at"):
                history.append({
                    "execution_id": execution_id,
                    "status": "running",
                    "timestamp": datetime.fromisoformat(execution_data["started_at"]),
                    "metadata": {"event": "execution_started"}
                })
            
            # Add completion event if completed
            if execution_data.get("completed_at"):
                history.append({
                    "execution_id": execution_id,
                    "status": execution_data["status"],
                    "timestamp": datetime.fromisoformat(execution_data["completed_at"]),
                    "metadata": {
                        "event": "execution_completed",
                        "execution_time_seconds": execution_data.get("execution_time_seconds"),
                        "error_message": execution_data.get("error_message")
                    }
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting execution history for {execution_id}: {str(e)}")
            return []
    
    async def get_execution_stats(self, user_id: str, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get execution statistics for a user
        
        Args:
            user_id: ID of the user
            workflow_id: Optional workflow ID to filter by
            
        Returns:
            Dictionary with execution statistics
        """
        try:
            result = await self.execution_crud.get_execution_stats(user_id, workflow_id)
            return result
        except Exception as e:
            logger.error(f"Error getting execution stats for user {user_id}: {str(e)}")
            return {"success": False, "error": str(e)}


# Global workflow status tracker instance
status_tracker = WorkflowStatusTracker()
