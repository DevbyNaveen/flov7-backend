"""
AI service endpoints for workflow generation.
Provides API endpoints for AI-powered workflow creation.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.ai.workflow_generator import workflow_generator
from app.primitives.validation import primitive_validator
import logging

# Configure logging
logger = logging.getLogger(__name__)

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
async def generate_workflow(request: WorkflowGenerationRequest):
    """
    Generate a workflow from a natural language prompt
    
    Args:
        request: Workflow generation request with prompt and user context
        
    Returns:
        Generated workflow definition and AI metadata
    """
    try:
        # Generate workflow using the AI service
        result = workflow_generator.create_workflow_from_prompt(
            request.prompt, 
            request.user_id or "anonymous"
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
        primitives = workflow_generator.openai_client  # This is incorrect, let me fix it
        # Let's import the primitive manager properly
        from app.primitives.primitives import primitive_manager
        return primitive_manager.get_all_primitives()
        
    except Exception as e:
        logger.error(f"Error retrieving primitives: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve primitives"
        )
