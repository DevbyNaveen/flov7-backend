"""
AI service endpoints for workflow generation.
Provides API endpoints for AI-powered workflow creation.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from app.ai.workflow_generator import workflow_generator
from app.primitives.validation import primitive_validator
from app.primitives.primitives import primitive_manager
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create router
router = APIRouter(
    prefix="/ai",
    tags=["AI Service"],
    responses={
        400: {"description": "Bad Request"},
        500: {"description": "Internal Server Error"}
    }
)


class WorkflowGenerationRequest(BaseModel):
    """Request model for workflow generation"""
    prompt: str
    user_id: Optional[str] = None


class WorkflowGenerationResponse(BaseModel):
    """Response model for workflow generation"""
    workflow: Dict[str, Any]
    ai_metadata: Optional[Dict[str, Any]] = None


@router.post("/generate", response_model=WorkflowGenerationResponse)
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute
async def generate_workflow(request: WorkflowGenerationRequest, http_request: Request):
    """
    Generate a workflow from a natural language prompt with database persistence
    
    Args:
        request: Workflow generation request with prompt and user context
        
    Returns:
        Generated workflow definition and AI metadata
    """
    try:
        # Generate workflow using the enhanced AI service
        result = await workflow_generator.create_workflow_from_prompt(
            prompt=request.prompt, 
            user_id=request.user_id or "anonymous",
            context=None,  # Could be enhanced with user context
            save_to_db=True
        )
        
        return WorkflowGenerationResponse(
            workflow=result["workflow"],
            ai_metadata=result["ai_metadata"]
        )
        
    except ValueError as e:
        logger.error(f"Validation error in workflow generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate workflow"
        )


@router.post("/validate")
async def validate_workflow(workflow_data: Dict[str, Any]):
    """
    Validate a workflow definition against the 5-primitives system
    
    Args:
        workflow_data: Workflow definition to validate
        
    Returns:
        Validation result with status and errors if any
    """
    try:
        # Validate workflow structure
        is_valid_structure = workflow_generator.validate_workflow_structure(workflow_data)
        
        if not is_valid_structure:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid workflow structure"
            )
        
        # Validate workflow primitives
        is_valid_primitives, error_message = primitive_validator.validate_workflow_primitives(workflow_data)
        
        if not is_valid_primitives:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message or "Invalid primitives in workflow"
            )
        
        return {
            "valid": True,
            "message": "Workflow is valid",
            "workflow_name": workflow_data.get("name", "Unknown")
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error validating workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate workflow"
        )


@router.get("/primitives")
async def get_primitives():
    """
    Get all available primitives in the 5-primitives system
    
    Returns:
        List of all available primitives with their definitions
    """
    try:
        return {
            "primitives": primitive_manager.get_all_primitives(),
            "total_count": len(primitive_manager.get_primitive_types()),
            "primitive_types": primitive_manager.get_primitive_types()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving primitives: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve primitives"
        )


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str, user_id: str):
    """
    Get a specific workflow from database
    
    Args:
        workflow_id: ID of the workflow to retrieve
        user_id: ID of the user requesting the workflow
        
    Returns:
        Workflow data from database
    """
    try:
        result = await workflow_generator.get_workflow_from_database(workflow_id, user_id)
        
        if result["success"]:
            return result["data"]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workflow"
        )


@router.get("/workflows")
async def list_workflows(
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None
):
    """
    List workflows for a user with pagination
    
    Args:
        user_id: ID of the user
        skip: Number of workflows to skip
        limit: Maximum number of workflows to return
        status: Filter by workflow status
        
    Returns:
        List of workflows with pagination info
    """
    try:
        result = await workflow_generator.list_user_workflows(user_id, skip, limit, status)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing workflows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list workflows"
        )


@router.put("/workflows/{workflow_id}")
async def update_workflow(
    workflow_id: str,
    user_id: str,
    update_data: Dict[str, Any]
):
    """
    Update a workflow in database
    
    Args:
        workflow_id: ID of the workflow to update
        user_id: ID of the user updating the workflow
        update_data: Data to update
        
    Returns:
        Updated workflow data
    """
    try:
        result = await workflow_generator.update_workflow_in_database(workflow_id, user_id, update_data)
        
        if result["success"]:
            return result["data"]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update workflow"
        )


@router.post("/workflows/{workflow_id}/regenerate")
async def regenerate_workflow(
    workflow_id: str,
    user_id: str,
    new_prompt: Optional[str] = None
):
    """
    Regenerate an existing workflow with improvements
    
    Args:
        workflow_id: ID of the workflow to regenerate
        user_id: ID of the user
        new_prompt: Optional new prompt for regeneration
        
    Returns:
        Regenerated workflow data
    """
    try:
        result = await workflow_generator.regenerate_workflow(workflow_id, user_id, new_prompt)
        
        if result["success"]:
            return {
                "workflow": result["workflow"],
                "ai_metadata": result["ai_metadata"],
                "message": "Workflow regenerated successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate workflow"
        )
