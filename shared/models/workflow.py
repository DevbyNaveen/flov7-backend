"""
Workflow data models for Flov7 platform.
Pydantic models for workflow-related data structures.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from uuid import UUID


class WorkflowBase(BaseModel):
    """Base workflow model"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    workflow_json: Dict[str, Any] = Field(default_factory=dict)
    tags: Optional[List[str]] = None
    is_template: bool = False


class WorkflowCreate(WorkflowBase):
    """Workflow creation model"""
    pass


class WorkflowUpdate(BaseModel):
    """Workflow update model"""
    name: Optional[str] = None
    description: Optional[str] = None
    workflow_json: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_template: Optional[bool] = None


class WorkflowInDB(WorkflowBase):
    """Workflow model as stored in database"""
    id: UUID
    user_id: UUID
    status: str = "draft"
    primitives_count: int = 0
    estimated_cost: float = 0.0
    execution_count: int = 0
    last_executed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    version: int = 1


class WorkflowResponse(WorkflowBase):
    """Workflow response model"""
    id: UUID
    user_id: UUID
    status: str
    primitives_count: int
    estimated_cost: float
    execution_count: int
    last_executed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


class WorkflowExecutionBase(BaseModel):
    """Base workflow execution model"""
    status: str = "pending"
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    temporal_workflow_id: Optional[str] = None


class WorkflowExecutionCreate(WorkflowExecutionBase):
    """Workflow execution creation model"""
    workflow_id: UUID


class WorkflowExecutionInDB(WorkflowExecutionBase):
    """Workflow execution model as stored in database"""
    id: UUID
    workflow_id: UUID
    user_id: UUID
    execution_time_seconds: Optional[float] = None
    cost_usd: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime


class WorkflowExecutionResponse(WorkflowExecutionBase):
    """Workflow execution response model"""
    id: UUID
    workflow_id: UUID
    user_id: UUID
    execution_time_seconds: Optional[float] = None
    cost_usd: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowTemplateBase(BaseModel):
    """Base workflow template model"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: str = "beginner"
    estimated_time_minutes: Optional[int] = None
    workflow_json: Dict[str, Any] = Field(default_factory=dict)
    preview_image_url: Optional[str] = None
    is_featured: bool = False


class WorkflowTemplateCreate(WorkflowTemplateBase):
    """Workflow template creation model"""
    pass


class WorkflowTemplateInDB(WorkflowTemplateBase):
    """Workflow template model as stored in database"""
    id: UUID
    usage_count: int = 0
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class WorkflowTemplateResponse(WorkflowTemplateBase):
    """Workflow template response model"""
    id: UUID
    usage_count: int
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
