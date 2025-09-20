"""
Primitive data models for Flov7 platform.
Pydantic models for the 5-primitives system.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class PrimitiveBase(BaseModel):
    """Base primitive model"""
    type: str = Field(..., description="Type of primitive: trigger, action, connection, condition, data")
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = None
    category: Optional[str] = None
    config_schema: Optional[Dict[str, Any]] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    is_active: bool = True
    is_beta: bool = False


class PrimitiveCreate(PrimitiveBase):
    """Primitive creation model"""
    pass


class PrimitiveUpdate(BaseModel):
    """Primitive update model"""
    type: Optional[str] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    category: Optional[str] = None
    config_schema: Optional[Dict[str, Any]] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_beta: Optional[bool] = None


class PrimitiveInDB(PrimitiveBase):
    """Primitive model as stored in database"""
    id: UUID
    created_at: datetime


class PrimitiveResponse(PrimitiveBase):
    """Primitive response model"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class PrimitiveTypes:
    """Enumeration of primitive types"""
    TRIGGER = "trigger"
    ACTION = "action"
    CONNECTION = "connection"
    CONDITION = "condition"
    DATA = "data"

    ALL = [TRIGGER, ACTION, CONNECTION, CONDITION, DATA]


class PrimitiveCategories:
    """Common primitive categories"""
    COMMUNICATION = "communication"
    DATA_PROCESSING = "data_processing"
    FILE_OPERATIONS = "file_operations"
    DATABASE = "database"
    WEBHOOKS = "webhooks"
    SCHEDULING = "scheduling"
    AI_OPERATIONS = "ai_operations"
    UTILITIES = "utilities"

    ALL = [COMMUNICATION, DATA_PROCESSING, FILE_OPERATIONS, DATABASE, WEBHOOKS, SCHEDULING, AI_OPERATIONS, UTILITIES]
