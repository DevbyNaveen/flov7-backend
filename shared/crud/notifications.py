"""
CRUD operations for notifications table.
Provides database operations for notification management with real-time capabilities.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from supabase import Client

from shared.config.database import db_manager


class NotificationCRUD:
    """CRUD operations for notifications"""
    
    def __init__(self):
        self.supabase = db_manager.get_client()
        self.service_supabase = db_manager.get_service_client()
    
    async def create_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new notification"""
        try:
            # Prepare notification data
            insert_data = {
                "user_id": notification_data["user_id"],
                "type": notification_data["type"],
                "title": notification_data["title"],
                "message": notification_data.get("message"),
                "data": notification_data.get("data", {}),
                "is_read": False
            }
            
            result = self.supabase.table("notifications").insert(insert_data).execute()
            
            if result.data:
                return {"success": True, "data": result.data[0]}
            else:
                return {"success": False, "error": "Failed to create notification"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_notification(self, notification_id: str, user_id: str) -> Dict[str, Any]:
        """Get notification by ID"""
        try:
            result = self.supabase.table("notifications").select("*").eq("id", notification_id).eq("user_id", user_id).execute()
            
            if result.data:
                return {"success": True, "data": result.data[0]}
            else:
                return {"success": False, "error": "Notification not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_notifications(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 20,
        unread_only: bool = False,
        notification_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """List notifications with pagination and filtering"""
        try:
            # Build query
            query = self.supabase.table("notifications").select("*").eq("user_id", user_id)
            
            # Apply filters
            if unread_only:
                query = query.eq("is_read", False)
            
            if notification_type:
                query = query.eq("type", notification_type)
            
            # Apply pagination and ordering
            result = query.order("created_at", desc=True).range(skip, skip + limit - 1).execute()
            
            # Get total count
            count_query = self.supabase.table("notifications").select("id", count="exact").eq("user_id", user_id)
            if unread_only:
                count_query = count_query.eq("is_read", False)
            if notification_type:
                count_query = count_query.eq("type", notification_type)
            
            count_result = count_query.execute()
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
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> Dict[str, Any]:
        """Mark a notification as read"""
        try:
            # Check if notification exists and belongs to user
            existing = await self.get_notification(notification_id, user_id)
            if not existing["success"]:
                return existing
            
            # Update notification
            result = self.supabase.table("notifications").update({
                "is_read": True,
                "read_at": datetime.utcnow().isoformat()
            }).eq("id", notification_id).execute()
            
            if result.data:
                return {"success": True, "data": result.data[0]}
            else:
                return {"success": False, "error": "Failed to update notification"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def mark_all_as_read(self, user_id: str, notification_type: Optional[str] = None) -> Dict[str, Any]:
        """Mark all notifications as read for a user"""
        try:
            # Build update query
            query = self.supabase.table("notifications").update({
                "is_read": True,
                "read_at": datetime.utcnow().isoformat()
            }).eq("user_id", user_id).eq("is_read", False)
            
            # Apply type filter if provided
            if notification_type:
                query = query.eq("type", notification_type)
            
            # Execute update
            result = query.execute()
            
            return {
                "success": True,
                "updated_count": len(result.data) if result.data else 0,
                "message": "Notifications marked as read"
            }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_notification(self, notification_id: str, user_id: str) -> Dict[str, Any]:
        """Delete a notification"""
        try:
            # Check if notification exists and belongs to user
            existing = await self.get_notification(notification_id, user_id)
            if not existing["success"]:
                return existing
            
            # Delete notification
            result = self.supabase.table("notifications").delete().eq("id", notification_id).execute()
            
            return {"success": True, "message": "Notification deleted successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_unread_count(self, user_id: str) -> Dict[str, Any]:
        """Get count of unread notifications for a user"""
        try:
            result = self.supabase.table("notifications").select("id", count="exact").eq("user_id", user_id).eq("is_read", False).execute()
            
            return {
                "success": True,
                "unread_count": result.count if result.count else 0
            }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_system_announcement(self, title: str, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create system announcement for all users (admin only)"""
        try:
            # Get all active users
            users_result = self.service_supabase.table("users").select("id").eq("is_active", True).execute()
            
            if not users_result.data:
                return {"success": False, "error": "No active users found"}
            
            # Create notification for each user
            notifications = []
            for user in users_result.data:
                notifications.append({
                    "user_id": user["id"],
                    "type": "system_announcement",
                    "title": title,
                    "message": message,
                    "data": data or {},
                    "is_read": False
                })
            
            # Batch insert notifications
            result = self.service_supabase.table("notifications").insert(notifications).execute()
            
            return {
                "success": True,
                "created_count": len(result.data) if result.data else 0,
                "message": "System announcement created successfully"
            }
                
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global notification CRUD instance
notification_crud = NotificationCRUD()
