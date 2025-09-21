"""
Workflow service endpoints for workflow execution.
Provides API endpoints for executing and monitoring workflows.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.workflow.executor import workflow_executor
from app.workflow.status import status_tracker
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/workflow",
    tags=["Workflow Service"],
    responses={
        400: {"description": "Bad Request"},
        500: {"description": "Internal Server Error"}
    }
)


class WorkflowExecutionRequest(BaseModel):
    """Request model for workflow execution"""
    workflow_data: Dict[str, Any]
    user_id: str


class WorkflowExecutionResponse(BaseModel):
    """Response model for workflow execution"""
    execution_id: str
    status: str
    workflow_id: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class WorkflowStatusResponse(BaseModel):
    """Response model for workflow status"""
    execution_id: str
    status: str
    workflow_id: Optional[str] = None
    updated_at: str
    metadata: Optional[Dict[str, Any]] = None


@router.post("/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(request: WorkflowExecutionRequest):
    """
    Execute a workflow definition
    
    Args:
        request: Workflow execution request with workflow data and user ID
        
    Returns:
        Workflow execution result
    """
    try:
        # Extract workflow_id from workflow_data if available
        workflow_id = request.workflow_data.get("id") or request.workflow_data.get("workflow_id")
        
        # Execute workflow
        result = await workflow_executor.execute_workflow(
            request.workflow_data,
            request.user_id
        )
        
        # Add workflow_id to result if available
        if workflow_id:
            result["workflow_id"] = workflow_id
        
        # Update status tracker with execution results
        await status_tracker.update_status(
            execution_id=result["execution_id"],
            status=result["status"],
            output_data=result.get("output_data"),
            error_message=result.get("error_message"),
            execution_time_seconds=result.get("execution_time_seconds")
        )
        
        return WorkflowExecutionResponse(**result)
        
    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute workflow"
        )


@router.get("/status/{execution_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(execution_id: str, user_id: str):
    """
    Get the status of a workflow execution
    
    Args:
        execution_id: ID of the workflow execution
        user_id: ID of the user (for security)
        
    Returns:
        Workflow execution status
    """
    try:
        status_info = await status_tracker.get_status(execution_id, user_id)
        
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow execution not found"
            )
        
        # Extract workflow_id from metadata if available
        workflow_id = None
        if status_info.get("metadata"):
            workflow_id = status_info["metadata"].get("workflow_id")
        
        return WorkflowStatusResponse(
            execution_id=execution_id,
            status=status_info["status"],
            workflow_id=workflow_id,
            updated_at=status_info["updated_at"].isoformat(),
            metadata=status_info.get("metadata")
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error retrieving workflow status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workflow status"
        )


@router.get("/history/{execution_id}")
async def get_execution_history(execution_id: str, user_id: str):
    """
    Get execution history for a workflow
    
    Args:
        execution_id: ID of the workflow execution
        user_id: ID of the user (for security)
        
    Returns:
        List of status updates in chronological order
    """
    try:
        history = await status_tracker.get_execution_history(execution_id, user_id)
        
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow execution history not found"
            )
        
        # Convert datetime objects to strings
        for entry in history:
            if "timestamp" in entry and entry["timestamp"]:
                entry["timestamp"] = entry["timestamp"].isoformat()
        
        return history
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error retrieving execution history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve execution history"
        )
