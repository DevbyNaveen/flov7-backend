"""
User management endpoints for Flov7 API Gateway
Handles user profile management, integrations, and role-based access control.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr

from app.auth.supabase_auth import supabase_auth
from app.auth.api_key_auth import get_api_key_data, require_api_permissions
from shared.config.database import db_manager

# Pydantic models for request/response
class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    subscription_plan: Optional[str] = None

class UserIntegrationCreate(BaseModel):
    service_name: str
    service_type: str  # api_key, oauth, webhook, database
    credentials: Dict[str, Any]

class UserIntegrationUpdate(BaseModel):
    credentials: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class NotificationCreate(BaseModel):
    type: str
    title: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class RoleUpdate(BaseModel):
    role: str  # admin, user, premium

# Create router
router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        422: {"description": "Validation Error"}
    }
)

# User Profile Management
@router.get("/profile", response_model=Dict[str, Any])
async def get_user_profile(
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Get current user's profile information"""
    try:
        supabase = db_manager.get_client()
        
        # Get user profile with additional stats
        user_result = supabase.table("users").select("*").eq("id", current_user["id"]).execute()
        
        if not user_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        user = user_result.data[0]
        
        # Get user statistics
        workflows_count = supabase.table("workflows").select("id", count="exact").eq("user_id", current_user["id"]).execute().count or 0
        executions_count = supabase.table("workflow_executions").select("id", count="exact").eq("user_id", current_user["id"]).execute().count or 0
        integrations_count = supabase.table("user_integrations").select("id", count="exact").eq("user_id", current_user["id"]).eq("is_active", True).execute().count or 0
        
        # Remove sensitive information
        user.pop("hashed_password", None)
        
        return {
            "user": user,
            "stats": {
                "workflows_count": workflows_count,
                "executions_count": executions_count,
                "integrations_count": integrations_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user profile: {str(e)}"
        )

@router.put("/profile", response_model=Dict[str, Any])
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Update current user's profile"""
    try:
        supabase = db_manager.get_client()
        
        # Build update data
        update_data = {}
        if profile_data.full_name is not None:
            update_data["full_name"] = profile_data.full_name
        if profile_data.avatar_url is not None:
            update_data["avatar_url"] = profile_data.avatar_url
        if profile_data.subscription_plan is not None:
            update_data["subscription_plan"] = profile_data.subscription_plan
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Update user profile
        result = supabase.table("users").update(update_data).eq("id", current_user["id"]).execute()
        
        if result.data:
            # Remove sensitive information
            user = result.data[0]
            user.pop("hashed_password", None)
            
            return {
                "success": True,
                "user": user,
                "message": "Profile updated successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update profile"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )

# User Integrations Management
@router.post("/integrations", response_model=Dict[str, Any])
async def create_user_integration(
    integration_data: UserIntegrationCreate,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Create a new user integration"""
    try:
        supabase = db_manager.get_client()
        
        # Check if integration already exists for this service
        existing = supabase.table("user_integrations").select("id").eq("user_id", current_user["id"]).eq("service_name", integration_data.service_name).execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Integration for {integration_data.service_name} already exists"
            )
        
        # Create integration
        result = supabase.table("user_integrations").insert({
            "user_id": current_user["id"],
            "service_name": integration_data.service_name,
            "service_type": integration_data.service_type,
            "credentials": integration_data.credentials,
            "is_active": True
        }).execute()
        
        if result.data:
            return {
                "success": True,
                "integration": result.data[0],
                "message": "Integration created successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create integration"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating integration: {str(e)}"
        )

@router.get("/integrations", response_model=Dict[str, Any])
async def list_user_integrations(
    include_inactive: bool = Query(False),
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """List user's integrations"""
    try:
        supabase = db_manager.get_client()
        
        # Build query
        query = supabase.table("user_integrations").select("*").eq("user_id", current_user["id"])
        
        if not include_inactive:
            query = query.eq("is_active", True)
        
        result = query.order("created_at", desc=True).execute()
        
        # Remove sensitive credential information from response
        integrations = []
        for integration in result.data:
            integration_copy = integration.copy()
            # Only show service info, not actual credentials
            integration_copy["credentials"] = {"configured": bool(integration["credentials"])}
            integrations.append(integration_copy)
        
        return {
            "integrations": integrations,
            "total": len(integrations)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching integrations: {str(e)}"
        )

@router.get("/integrations/{integration_id}", response_model=Dict[str, Any])
async def get_user_integration(
    integration_id: UUID,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Get a specific integration"""
    try:
        supabase = db_manager.get_client()
        
        result = supabase.table("user_integrations").select("*").eq("id", str(integration_id)).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
        integration = result.data[0]
        # Remove sensitive credential information
        integration["credentials"] = {"configured": bool(integration["credentials"])}
        
        return {
            "integration": integration
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching integration: {str(e)}"
        )

@router.put("/integrations/{integration_id}", response_model=Dict[str, Any])
async def update_user_integration(
    integration_id: UUID,
    integration_data: UserIntegrationUpdate,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Update a user integration"""
    try:
        supabase = db_manager.get_client()
        
        # Check if integration exists and belongs to user
        existing = supabase.table("user_integrations").select("*").eq("id", str(integration_id)).eq("user_id", current_user["id"]).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
        # Build update data
        update_data = {}
        if integration_data.credentials is not None:
            update_data["credentials"] = integration_data.credentials
        if integration_data.is_active is not None:
            update_data["is_active"] = integration_data.is_active
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Update integration
        result = supabase.table("user_integrations").update(update_data).eq("id", str(integration_id)).execute()
        
        if result.data:
            integration = result.data[0]
            # Remove sensitive credential information
            integration["credentials"] = {"configured": bool(integration["credentials"])}
            
            return {
                "success": True,
                "integration": integration,
                "message": "Integration updated successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update integration"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating integration: {str(e)}"
        )

@router.delete("/integrations/{integration_id}")
async def delete_user_integration(
    integration_id: UUID,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Delete a user integration"""
    try:
        supabase = db_manager.get_client()
        
        # Check if integration exists and belongs to user
        existing = supabase.table("user_integrations").select("id").eq("id", str(integration_id)).eq("user_id", current_user["id"]).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
        # Delete integration
        result = supabase.table("user_integrations").delete().eq("id", str(integration_id)).execute()
        
        return {
            "success": True,
            "message": "Integration deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting integration: {str(e)}"
        )

# Notifications Management
@router.get("/notifications", response_model=Dict[str, Any])
async def get_user_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Get user notifications"""
    try:
        supabase = db_manager.get_client()
        
        # Build query
        query = supabase.table("notifications").select("*").eq("user_id", current_user["id"])
        
        if unread_only:
            query = query.eq("is_read", False)
        
        # Apply pagination and ordering
        result = query.order("created_at", desc=True).range(skip, skip + limit - 1).execute()
        
        # Get unread count
        unread_count = supabase.table("notifications").select("id", count="exact").eq("user_id", current_user["id"]).eq("is_read", False).execute().count or 0
        
        return {
            "notifications": result.data,
            "unread_count": unread_count,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching notifications: {str(e)}"
        )

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Mark a notification as read"""
    try:
        supabase = db_manager.get_client()
        
        # Check if notification exists and belongs to user
        existing = supabase.table("notifications").select("id").eq("id", str(notification_id)).eq("user_id", current_user["id"]).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Mark as read
        result = supabase.table("notifications").update({
            "is_read": True,
            "read_at": datetime.utcnow().isoformat()
        }).eq("id", str(notification_id)).execute()
        
        return {
            "success": True,
            "message": "Notification marked as read"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking notification as read: {str(e)}"
        )

@router.put("/notifications/read-all")
async def mark_all_notifications_read(
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Mark all notifications as read"""
    try:
        supabase = db_manager.get_client()
        
        # Mark all unread notifications as read
        result = supabase.table("notifications").update({
            "is_read": True,
            "read_at": datetime.utcnow().isoformat()
        }).eq("user_id", current_user["id"]).eq("is_read", False).execute()
        
        return {
            "success": True,
            "message": "All notifications marked as read"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking notifications as read: {str(e)}"
        )

# Admin endpoints (require admin role)
@router.get("/admin/users", response_model=Dict[str, Any])
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """List all users (admin only)"""
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        supabase = db_manager.get_service_client()
        
        # Build query
        query = supabase.table("users").select("id, email, full_name, role, is_active, created_at, last_login, subscription_plan")
        
        # Apply filters
        if role:
            query = query.eq("role", role)
        if is_active is not None:
            query = query.eq("is_active", is_active)
        
        # Apply pagination and ordering
        result = query.order("created_at", desc=True).range(skip, skip + limit - 1).execute()
        
        # Get total count
        count_result = supabase.table("users").select("id", count="exact").execute()
        total_count = count_result.count if count_result.count else 0
        
        return {
            "users": result.data,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "has_more": total_count > skip + limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )

@router.put("/admin/users/{user_id}/role", response_model=Dict[str, Any])
async def update_user_role(
    user_id: UUID,
    role_data: RoleUpdate,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Update user role (admin only)"""
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Validate role
    valid_roles = ["admin", "user", "premium"]
    if role_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    try:
        supabase = db_manager.get_service_client()
        
        # Check if user exists
        existing = supabase.table("users").select("id, email, role").eq("id", str(user_id)).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update user role
        result = supabase.table("users").update({
            "role": role_data.role
        }).eq("id", str(user_id)).execute()
        
        if result.data:
            user = result.data[0]
            user.pop("hashed_password", None)
            
            return {
                "success": True,
                "user": user,
                "message": f"User role updated to {role_data.role}"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update user role"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user role: {str(e)}"
        )

@router.put("/admin/users/{user_id}/status")
async def update_user_status(
    user_id: UUID,
    is_active: bool,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Activate/deactivate user (admin only)"""
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        supabase = db_manager.get_service_client()
        
        # Check if user exists
        existing = supabase.table("users").select("id, email").eq("id", str(user_id)).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update user status
        result = supabase.table("users").update({
            "is_active": is_active
        }).eq("id", str(user_id)).execute()
        
        status_text = "activated" if is_active else "deactivated"
        
        return {
            "success": True,
            "message": f"User {status_text} successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user status: {str(e)}"
        )

# Health check
@router.get("/health")
async def users_health_check():
    """Health check for user endpoints"""
    return {
        "status": "healthy",
        "service": "users",
        "features": [
            "profile_management",
            "integrations_management",
            "notifications",
            "role_based_access_control",
            "admin_functions"
        ]
    }
