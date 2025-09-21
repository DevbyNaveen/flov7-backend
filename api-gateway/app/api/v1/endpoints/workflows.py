"""
Workflow endpoints for Flov7 API Gateway
Handles workflow CRUD operations, execution, and management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from app.auth.supabase_auth import supabase_auth
from app.auth.api_key_auth import get_api_key_data, require_api_permissions
from shared.config.database import db_manager
from shared.crud.workflows import workflow_crud
from shared.crud.executions import execution_crud

# Pydantic models for request/response
class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    workflow_json: Dict[str, Any]
    tags: Optional[List[str]] = None
    is_template: bool = False

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    workflow_json: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None

class WorkflowExecutionRequest(BaseModel):
    input_data: Optional[Dict[str, Any]] = None

class WorkflowResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    status: str
    workflow_json: Dict[str, Any]
    primitives_count: int
    estimated_cost: float
    execution_count: int
    last_executed_at: Optional[datetime]
    is_template: bool
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    version: int

# Create router
router = APIRouter(
    prefix="/workflows",
    tags=["Workflows"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        422: {"description": "Validation Error"}
    }
)

# Workflow CRUD Operations
@router.post("/", response_model=Dict[str, Any])
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Create a new workflow"""
    try:
        # Prepare workflow data for CRUD operation
        db_workflow_data = {
            "name": workflow_data.name,
            "description": workflow_data.description,
            "workflow_json": workflow_data.workflow_json,
            "tags": workflow_data.tags or [],
            "is_template": workflow_data.is_template,
            "status": "draft"
        }
        
        # Use workflow CRUD to create workflow
        result = await workflow_crud.create_workflow(current_user["id"], db_workflow_data)
        
        if result["success"]:
            return {
                "success": True,
                "workflow": result["data"],
                "message": "Workflow created successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating workflow: {str(e)}"
        )

@router.get("/", response_model=Dict[str, Any])
async def list_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """List user's workflows with pagination and filtering"""
    try:
        # Parse tags if provided
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
        
        # Use workflow CRUD to list workflows
        result = await workflow_crud.list_workflows(
            user_id=current_user["id"],
            skip=skip,
            limit=limit,
            status=status,
            tags=tag_list
        )
        
        if result["success"]:
            return {
                "workflows": result["data"],
                "total": result["total"],
                "skip": result["skip"],
                "limit": result["limit"],
                "has_more": result["has_more"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching workflows: {str(e)}"
        )

@router.get("/{workflow_id}", response_model=Dict[str, Any])
async def get_workflow(
    workflow_id: UUID,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Get a specific workflow by ID"""
    try:
        # Use workflow CRUD to get workflow
        result = await workflow_crud.get_workflow(str(workflow_id), current_user["id"])
        
        if result["success"]:
            return {
                "workflow": result["data"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching workflow: {str(e)}"
        )

@router.put("/{workflow_id}", response_model=Dict[str, Any])
async def update_workflow(
    workflow_id: UUID,
    workflow_data: WorkflowUpdate,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Update a workflow"""
    try:
        # Build update data
        update_data = {}
        if workflow_data.name is not None:
            update_data["name"] = workflow_data.name
        if workflow_data.description is not None:
            update_data["description"] = workflow_data.description
        if workflow_data.workflow_json is not None:
            update_data["workflow_json"] = workflow_data.workflow_json
        if workflow_data.status is not None:
            update_data["status"] = workflow_data.status
        if workflow_data.tags is not None:
            update_data["tags"] = workflow_data.tags
        
        # Use workflow CRUD to update workflow
        result = await workflow_crud.update_workflow(str(workflow_id), current_user["id"], update_data)
        
        if result["success"]:
            return {
                "success": True,
                "workflow": result["data"],
                "message": "Workflow updated successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating workflow: {str(e)}"
        )

@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: UUID,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Delete a workflow"""
    try:
        # Use workflow CRUD to delete workflow
        result = await workflow_crud.delete_workflow(str(workflow_id), current_user["id"])
        
        if result["success"]:
            return {
                "success": True,
                "message": "Workflow deleted successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting workflow: {str(e)}"
        )

# Workflow Execution Operations
@router.post("/{workflow_id}/execute", response_model=Dict[str, Any])
async def execute_workflow(
    workflow_id: UUID,
    execution_data: WorkflowExecutionRequest,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Execute a workflow"""
    try:
        # Check if workflow exists and belongs to user
        workflow_result = await workflow_crud.get_workflow(str(workflow_id), current_user["id"])
        
        if not workflow_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        workflow = workflow_result["data"]
        
        # Create execution record using execution_crud
        execution_data_db = {
            "workflow_id": str(workflow_id),
            "user_id": current_user["id"],
            "status": "pending",
            "input_data": execution_data.input_data or {},
            "started_at": datetime.utcnow().isoformat()
        }
        
        execution_result = await execution_crud.create_execution(execution_data_db)
        
        if not execution_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=execution_result["error"]
            )
        
        execution = execution_result["data"]
        
        # TODO: Integrate with workflow service for actual execution
        # For now, we'll return the execution ID and mark it as pending
        
        # Update workflow execution count
        await workflow_crud.increment_execution_count(str(workflow_id))
        
        return {
            "success": True,
            "execution_id": execution["id"],
            "status": "pending",
            "message": "Workflow execution started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing workflow: {str(e)}"
        )

@router.get("/{workflow_id}/executions", response_model=Dict[str, Any])
async def get_workflow_executions(
    workflow_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Get execution history for a workflow"""
    try:
        # Check if workflow exists and belongs to user
        workflow_result = await workflow_crud.get_workflow(str(workflow_id), current_user["id"])
        
        if not workflow_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Get executions using execution_crud
        result = await execution_crud.list_executions(
            user_id=current_user["id"],
            workflow_id=str(workflow_id),
            skip=skip,
            limit=limit
        )
        
        if result["success"]:
            return {
                "executions": result["data"],
                "total": result["total"],
                "skip": result["skip"],
                "limit": result["limit"],
                "has_more": result["has_more"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching executions: {str(e)}"
        )

@router.get("/executions/{execution_id}", response_model=Dict[str, Any])
async def get_execution_status(
    execution_id: UUID,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Get status of a specific execution"""
    try:
        # Use execution_crud to get execution
        result = await execution_crud.get_execution(str(execution_id), current_user["id"])
        
        if result["success"]:
            return {
                "execution": result["data"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching execution: {str(e)}"
        )

# Workflow Templates
@router.get("/templates/", response_model=Dict[str, Any])
async def list_workflow_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    featured: Optional[bool] = Query(None)
):
    """List available workflow templates"""
    try:
        supabase = db_manager.get_client()
        
        # Build query
        query = supabase.table("workflow_templates").select("*")
        
        # Apply filters
        if category:
            query = query.eq("category", category)
        if difficulty:
            query = query.eq("difficulty", difficulty)
        if featured is not None:
            query = query.eq("is_featured", featured)
        
        # Apply pagination and ordering
        result = query.order("usage_count", desc=True).range(skip, skip + limit - 1).execute()
        
        # Get total count
        count_result = supabase.table("workflow_templates").select("id", count="exact").execute()
        total_count = count_result.count if count_result.count else 0
        
        return {
            "templates": result.data,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "has_more": total_count > skip + limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching templates: {str(e)}"
        )

@router.post("/templates/{template_id}/use", response_model=Dict[str, Any])
async def use_workflow_template(
    template_id: UUID,
    workflow_name: str,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Create a workflow from a template"""
    try:
        supabase = db_manager.get_client()
        
        # Get template
        template_result = supabase.table("workflow_templates").select("*").eq("id", str(template_id)).execute()
        
        if not template_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        template = template_result.data[0]
        
        # Create workflow from template
        workflow_result = supabase.table("workflows").insert({
            "user_id": current_user["id"],
            "name": workflow_name,
            "description": f"Created from template: {template['name']}",
            "workflow_json": template["workflow_json"],
            "primitives_count": len(template["workflow_json"].get("primitives", [])),
            "status": "draft"
        }).execute()
        
        if not workflow_result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create workflow from template"
            )
        
        # Update template usage count
        supabase.table("workflow_templates").update({
            "usage_count": template["usage_count"] + 1
        }).eq("id", str(template_id)).execute()
        
        return {
            "success": True,
            "workflow": workflow_result.data[0],
            "message": "Workflow created from template successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating workflow from template: {str(e)}"
        )

# Health check
@router.get("/health")
async def workflows_health_check():
    """Health check for workflow endpoints"""
    return {
        "status": "healthy",
        "service": "workflows",
        "features": [
            "crud_operations",
            "execution_tracking",
            "template_support",
            "pagination",
            "filtering"
        ]
    }
