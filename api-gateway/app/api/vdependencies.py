"""
API dependencies for Flov7 API Gateway.
Common dependencies used across API endpoints.
"""

from fastapi import Depends, HTTPException, status
from typing import Dict, Any, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)


# Dependency for getting current user
async def get_current_user(token: str) -> Dict[str, Any]:
    """
    Dependency to get current user from token
    
    Args:
        token: Authentication token
        
    Returns:
        User information dictionary
        
    Raises:
        HTTPException: If user is not authenticated
    """
    # In a real implementation, this would validate the token and return user info
    # For now, we'll return mock user data
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "user_id": "mock-user-id",
        "email": "user@example.com",
        "full_name": "Mock User"
    }


# Dependency for rate limiting
async def rate_limit_dependency(request_count: int = Depends(lambda: 0)) -> bool:
    """
    Dependency to implement rate limiting
    
    Args:
        request_count: Number of requests (mock implementation)
        
    Returns:
        Boolean indicating if request is allowed
        
    Raises:
        HTTPException: If rate limit is exceeded
    """
    # In a real implementation, this would check request rate against limits
    # For now, we'll allow all requests
    max_requests_per_minute = 100
    
    if request_count > max_requests_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )
    
    return True


# Dependency for validating workflow data
async def validate_workflow_data(workflow_data: Dict[str, Any]) -> bool:
    """
    Dependency to validate workflow data structure
    
    Args:
        workflow_data: Workflow data to validate
        
    Returns:
        Boolean indicating if workflow data is valid
        
    Raises:
        HTTPException: If workflow data is invalid
    """
    # Check required fields
    required_fields = ["name", "nodes", "edges"]
    for field in required_fields:
        if field not in workflow_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field in workflow data: {field}",
            )
    
    # Validate nodes structure
    nodes = workflow_data.get("nodes", [])
    if not isinstance(nodes, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid nodes structure in workflow data",
        )
    
    # Validate edges structure
    edges = workflow_data.get("edges", [])
    if not isinstance(edges, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid edges structure in workflow data",
        )
    
    return True
