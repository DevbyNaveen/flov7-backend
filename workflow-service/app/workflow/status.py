"""
Workflow status tracking for Flov7 workflow service.
Handles monitoring and status updates for workflow executions.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from shared.constants.status import EXECUTION_STATUSES, EXECUTION_STATUS_COMPLETED, EXECUTION_STATUS_FAILED
from shared.models.workflow import WorkflowExecutionResponse
import logging

# Configure logging
logger = logging.getLogger(__name__)


class WorkflowStatusTracker:
    """Workflow execution status tracker"""
    
    def __init__(self):
        self.statuses = {}
    
    def update_status(self, execution_id: str, status: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update the status of a workflow execution
        
        Args:
            execution_id: ID of the workflow execution
            status: New status value
            metadata: Optional metadata to store with status
            
        Returns:
            Boolean indicating success
        """
        if status not in EXECUTION_STATUSES:
            logger.warning(f"Invalid status '{status}' for execution {execution_id}")
            return False
        
        self.statuses[execution_id] = {
            "status": status,
            "updated_at": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        logger.info(f"Updated status for execution {execution_id} to {status}")
        return True
    
    def get_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a workflow execution
        
        Args:
            execution_id: ID of the workflow execution
            
        Returns:
            Status information or None if not found
        """
        return self.statuses.get(execution_id)
    
    def get_all_statuses(self) -> Dict[str, Any]:
        """
        Get all workflow execution statuses
        
        Returns:
            Dictionary of all execution statuses
        """
        return self.statuses
    
    def is_execution_completed(self, execution_id: str) -> bool:
        """
        Check if a workflow execution is completed
        
        Args:
            execution_id: ID of the workflow execution
            
        Returns:
            Boolean indicating if execution is completed
        """
        status_info = self.statuses.get(execution_id)
        if not status_info:
            return False
        
        return status_info["status"] in [EXECUTION_STATUS_COMPLETED, EXECUTION_STATUS_FAILED]
    
    def get_execution_history(self, execution_id: str) -> List[Dict[str, Any]]:
        """
        Get execution history for a workflow
        
        Args:
            execution_id: ID of the workflow execution
            
        Returns:
            List of status updates in chronological order
        """
        # In a real implementation, this would query a database
        # For now, we'll return a simple history based on current status
        status_info = self.statuses.get(execution_id)
        if not status_info:
            return []
        
        return [{
            "execution_id": execution_id,
            "status": status_info["status"],
            "timestamp": status_info["updated_at"],
            "metadata": status_info["metadata"]
        }]


# Global workflow status tracker instance
status_tracker = WorkflowStatusTracker()
