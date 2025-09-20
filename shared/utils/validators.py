"""
Validation utilities for Flov7 platform.
Custom validators for data models and API inputs.
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, ValidationError, validator, field_validator
import re


def validate_workflow_json(workflow_data: Dict[str, Any]) -> bool:
    """Validate workflow JSON structure"""
    required_keys = ['name', 'nodes', 'edges']
    
    # Check if all required keys are present
    for key in required_keys:
        if key not in workflow_data:
            return False
    
    # Validate nodes structure
    if not isinstance(workflow_data['nodes'], list):
        return False
    
    # Validate edges structure
    if not isinstance(workflow_data['edges'], list):
        return False
    
    return True


def validate_primitive_type(primitive_type: str) -> bool:
    """Validate primitive type"""
    valid_types = ['trigger', 'action', 'connection', 'condition', 'data']
    return primitive_type in valid_types


def validate_primitive_schema(schema_data: Dict[str, Any]) -> bool:
    """Validate primitive schema structure"""
    # Basic schema validation
    if not isinstance(schema_data, dict):
        return False
    
    # Check for required fields in schema
    return True


def validate_api_key_permissions(permissions: Dict[str, Any]) -> bool:
    """Validate API key permissions structure"""
    if not isinstance(permissions, dict):
        return False
    
    # Validate permission structure
    return True


def validate_user_role(role: str) -> bool:
    """Validate user role"""
    valid_roles = ['user', 'admin', 'premium']
    return role in valid_roles


def validate_subscription_plan(plan: str) -> bool:
    """Validate subscription plan"""
    valid_plans = ['free', 'basic', 'pro', 'enterprise']
    return plan in valid_plans


def validate_workflow_status(status: str) -> bool:
    """Validate workflow status"""
    valid_statuses = ['draft', 'active', 'inactive', 'archived']
    return status in valid_statuses


def validate_execution_status(status: str) -> bool:
    """Validate workflow execution status"""
    valid_statuses = ['pending', 'running', 'completed', 'failed']
    return status in valid_statuses


def validate_deployment_platform(platform: str) -> bool:
    """Validate deployment platform"""
    valid_platforms = ['vercel', 'railway', 'render', 'aws', 'gcp', 'azure']
    return platform in valid_platforms


def validate_deployment_status(status: str) -> bool:
    """Validate deployment status"""
    valid_statuses = ['pending', 'deploying', 'active', 'failed']
    return status in valid_statuses


def validate_tags(tags: List[str]) -> bool:
    """Validate tags list"""
    if not isinstance(tags, list):
        return False
    
    # Check each tag
    for tag in tags:
        if not isinstance(tag, str) or len(tag) == 0 or len(tag) > 50:
            return False
    
    return True


def validate_url(url: str) -> bool:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None


def validate_json_schema(schema: Dict[str, Any]) -> bool:
    """Validate JSON schema structure"""
    # Basic validation of JSON schema
    if not isinstance(schema, dict):
        return False
    
    # Check for basic schema structure
    return True
