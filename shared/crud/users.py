"""
CRUD operations for users table.
Provides database operations for user management.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from supabase import Client

from shared.config.database import db_manager


class UserCRUD:
    """CRUD operations for users"""
    
    def __init__(self):
        self.supabase = db_manager.get_client()
        self.service_supabase = db_manager.get_service_client()
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile by ID"""
        try:
            result = self.supabase.table("users").select("*").eq("id", user_id).execute()
            
            if result.data:
                user = result.data[0]
                # Remove sensitive information
                user.pop("hashed_password", None)
                return {"success": True, "data": user}
            else:
                return {"success": False, "error": "User not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_user_profile(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        try:
            # Prepare update data
            filtered_update = {}
            allowed_fields = ["full_name", "avatar_url", "subscription_plan"]
            
            for field in allowed_fields:
                if field in update_data:
                    filtered_update[field] = update_data[field]
            
            if not filtered_update:
                return {"success": False, "error": "No valid fields to update"}
            
            # Update user profile
            result = self.supabase.table("users").update(filtered_update).eq("id", user_id).execute()
            
            if result.data:
                user = result.data[0]
                # Remove sensitive information
                user.pop("hashed_password", None)
                return {"success": True, "data": user}
            else:
                return {"success": False, "error": "Failed to update profile"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_last_login(self, user_id: str) -> Dict[str, Any]:
        """Update user's last login timestamp"""
        try:
            result = self.supabase.table("users").update({
                "last_login": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            if result.data:
                return {"success": True, "data": result.data[0]}
            else:
                return {"success": False, "error": "Failed to update last login"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            # Get workflow count
            workflows_result = self.supabase.table("workflows").select("id", count="exact").eq("user_id", user_id).execute()
            
            # Get execution count
            executions_result = self.supabase.table("workflow_executions").select("id", count="exact").eq("user_id", user_id).execute()
            
            # Get active integrations count
            integrations_result = self.supabase.table("user_integrations").select("id", count="exact").eq("user_id", user_id).eq("is_active", True).execute()
            
            # Get unread notifications count
            notifications_result = self.supabase.table("notifications").select("id", count="exact").eq("user_id", user_id).eq("is_read", False).execute()
            
            return {
                "success": True,
                "data": {
                    "workflows_count": workflows_result.count or 0,
                    "executions_count": executions_result.count or 0,
                    "integrations_count": integrations_result.count or 0,
                    "unread_notifications": notifications_result.count or 0
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Admin functions
    async def list_all_users(
        self, 
        skip: int = 0, 
        limit: int = 50,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """List all users (admin only)"""
        try:
            # Build query
            query = self.service_supabase.table("users").select("id, email, full_name, role, is_active, created_at, last_login, subscription_plan")
            
            # Apply filters
            if role:
                query = query.eq("role", role)
            if is_active is not None:
                query = query.eq("is_active", is_active)
            
            # Apply pagination and ordering
            result = query.order("created_at", desc=True).range(skip, skip + limit - 1).execute()
            
            # Get total count
            count_result = self.service_supabase.table("users").select("id", count="exact").execute()
            total_count = count_result.count if count_result.count else 0
            
            return {
                "success": True,
                "data": result.data,
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "has_more": total_count > skip + limit
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_user_role(self, user_id: str, role: str) -> Dict[str, Any]:
        """Update user role (admin only)"""
        try:
            # Validate role
            valid_roles = ["admin", "user", "premium"]
            if role not in valid_roles:
                return {"success": False, "error": f"Invalid role. Must be one of: {', '.join(valid_roles)}"}
            
            # Check if user exists
            existing = self.service_supabase.table("users").select("id, email, role").eq("id", user_id).execute()
            
            if not existing.data:
                return {"success": False, "error": "User not found"}
            
            # Update user role
            result = self.service_supabase.table("users").update({"role": role}).eq("id", user_id).execute()
            
            if result.data:
                user = result.data[0]
                user.pop("hashed_password", None)
                return {"success": True, "data": user}
            else:
                return {"success": False, "error": "Failed to update user role"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_user_status(self, user_id: str, is_active: bool) -> Dict[str, Any]:
        """Update user active status (admin only)"""
        try:
            # Check if user exists
            existing = self.service_supabase.table("users").select("id, email").eq("id", user_id).execute()
            
            if not existing.data:
                return {"success": False, "error": "User not found"}
            
            # Update user status
            result = self.service_supabase.table("users").update({"is_active": is_active}).eq("id", user_id).execute()
            
            if result.data:
                return {"success": True, "message": f"User {'activated' if is_active else 'deactivated'} successfully"}
            else:
                return {"success": False, "error": "Failed to update user status"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}


class UserIntegrationCRUD:
    """CRUD operations for user integrations"""
    
    def __init__(self):
        self.supabase = db_manager.get_client()
    
    async def create_integration(self, user_id: str, integration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user integration"""
        try:
            # Check if integration already exists for this service
            existing = self.supabase.table("user_integrations").select("id").eq("user_id", user_id).eq("service_name", integration_data["service_name"]).execute()
            
            if existing.data:
                return {"success": False, "error": f"Integration for {integration_data['service_name']} already exists"}
            
            # Create integration
            insert_data = {
                "user_id": user_id,
                "service_name": integration_data["service_name"],
                "service_type": integration_data["service_type"],
                "credentials": integration_data["credentials"],
                "is_active": True
            }
            
            result = self.supabase.table("user_integrations").insert(insert_data).execute()
            
            if result.data:
                return {"success": True, "data": result.data[0]}
            else:
                return {"success": False, "error": "Failed to create integration"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_integrations(self, user_id: str, include_inactive: bool = False) -> Dict[str, Any]:
        """List user integrations"""
        try:
            # Build query
            query = self.supabase.table("user_integrations").select("*").eq("user_id", user_id)
            
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
                "success": True,
                "data": integrations,
                "total": len(integrations)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_integration(self, integration_id: str, user_id: str) -> Dict[str, Any]:
        """Get a specific integration"""
        try:
            result = self.supabase.table("user_integrations").select("*").eq("id", integration_id).eq("user_id", user_id).execute()
            
            if result.data:
                integration = result.data[0]
                # Remove sensitive credential information
                integration["credentials"] = {"configured": bool(integration["credentials"])}
                return {"success": True, "data": integration}
            else:
                return {"success": False, "error": "Integration not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_integration(self, integration_id: str, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user integration"""
        try:
            # Check if integration exists and belongs to user
            existing = self.supabase.table("user_integrations").select("*").eq("id", integration_id).eq("user_id", user_id).execute()
            
            if not existing.data:
                return {"success": False, "error": "Integration not found"}
            
            # Prepare update data
            filtered_update = {}
            allowed_fields = ["credentials", "is_active"]
            
            for field in allowed_fields:
                if field in update_data:
                    filtered_update[field] = update_data[field]
            
            if not filtered_update:
                return {"success": False, "error": "No valid fields to update"}
            
            # Update integration
            result = self.supabase.table("user_integrations").update(filtered_update).eq("id", integration_id).execute()
            
            if result.data:
                integration = result.data[0]
                # Remove sensitive credential information
                integration["credentials"] = {"configured": bool(integration["credentials"])}
                return {"success": True, "data": integration}
            else:
                return {"success": False, "error": "Failed to update integration"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_integration(self, integration_id: str, user_id: str) -> Dict[str, Any]:
        """Delete a user integration"""
        try:
            # Check if integration exists and belongs to user
            existing = self.supabase.table("user_integrations").select("id").eq("id", integration_id).eq("user_id", user_id).execute()
            
            if not existing.data:
                return {"success": False, "error": "Integration not found"}
            
            # Delete integration
            result = self.supabase.table("user_integrations").delete().eq("id", integration_id).execute()
            
            return {"success": True, "message": "Integration deleted successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}


class NotificationCRUD:
    """CRUD operations for notifications"""
    
    def __init__(self):
        self.supabase = db_manager.get_client()
        self.service_supabase = db_manager.get_service_client()
    
    async def create_notification(self, user_id: str, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new notification"""
        try:
            insert_data = {
                "user_id": user_id,
                "type": notification_data["type"],
                "title": notification_data["title"],
                "message": notification_data.get("message"),
                "data": notification_data.get("data", {})
            }
            
            result = self.supabase.table("notifications").insert(insert_data).execute()
            
            if result.data:
                return {"success": True, "data": result.data[0]}
            else:
                return {"success": False, "error": "Failed to create notification"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_notifications(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 20,
        unread_only: bool = False
    ) -> Dict[str, Any]:
        """List user notifications"""
        try:
            # Build query
            query = self.supabase.table("notifications").select("*").eq("user_id", user_id)
            
            if unread_only:
                query = query.eq("is_read", False)
            
            # Apply pagination and ordering
            result = query.order("created_at", desc=True).range(skip, skip + limit - 1).execute()
            
            # Get unread count
            unread_count = self.supabase.table("notifications").select("id", count="exact").eq("user_id", user_id).eq("is_read", False).execute().count or 0
            
            return {
                "success": True,
                "data": result.data,
                "unread_count": unread_count,
                "skip": skip,
                "limit": limit
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def mark_notification_read(self, notification_id: str, user_id: str) -> Dict[str, Any]:
        """Mark a notification as read"""
        try:
            # Check if notification exists and belongs to user
            existing = self.supabase.table("notifications").select("id").eq("id", notification_id).eq("user_id", user_id).execute()
            
            if not existing.data:
                return {"success": False, "error": "Notification not found"}
            
            # Mark as read
            result = self.supabase.table("notifications").update({
                "is_read": True,
                "read_at": datetime.utcnow().isoformat()
            }).eq("id", notification_id).execute()
            
            return {"success": True, "message": "Notification marked as read"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def mark_all_notifications_read(self, user_id: str) -> Dict[str, Any]:
        """Mark all notifications as read"""
        try:
            # Mark all unread notifications as read
            result = self.supabase.table("notifications").update({
                "is_read": True,
                "read_at": datetime.utcnow().isoformat()
            }).eq("user_id", user_id).eq("is_read", False).execute()
            
            return {"success": True, "message": "All notifications marked as read"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global CRUD instances
user_crud = UserCRUD()
user_integration_crud = UserIntegrationCRUD()
notification_crud = NotificationCRUD()
