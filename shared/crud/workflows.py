"""
CRUD operations for workflows table.
Provides database operations for workflow management.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from supabase import Client

from shared.config.database import db_manager


class WorkflowCRUD:
    """CRUD operations for workflows"""
    
    def __init__(self):
        self.supabase = db_manager.get_client()
        self.service_supabase = db_manager.get_service_client()
    
    async def create_workflow(self, user_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow"""
        try:
            # Calculate primitives count
            primitives_count = len(workflow_data.get("workflow_json", {}).get("primitives", []))
            
            # Prepare workflow data
            insert_data = {
                "user_id": user_id,
                "name": workflow_data["name"],
                "description": workflow_data.get("description"),
                "workflow_json": workflow_data["workflow_json"],
                "primitives_count": primitives_count,
                "tags": workflow_data.get("tags", []),
                "is_template": workflow_data.get("is_template", False),
                "status": workflow_data.get("status", "draft")
            }
            
            result = self.supabase.table("workflows").insert(insert_data).execute()
            
            if result.data:
                return {"success": True, "data": result.data[0]}
            else:
                return {"success": False, "error": "Failed to create workflow"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_workflow(self, workflow_id: str, user_id: str) -> Dict[str, Any]:
        """Get a workflow by ID"""
        try:
            result = self.supabase.table("workflows").select("*").eq("id", workflow_id).eq("user_id", user_id).execute()
            
            if result.data:
                return {"success": True, "data": result.data[0]}
            else:
                return {"success": False, "error": "Workflow not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_workflows(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 50,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List workflows with pagination and filtering"""
        try:
            # Build query
            query = self.supabase.table("workflows").select("*").eq("user_id", user_id)
            
            # Apply filters
            if status:
                query = query.eq("status", status)
            
            if tags:
                query = query.contains("tags", tags)
            
            # Apply pagination and ordering
            result = query.order("updated_at", desc=True).range(skip, skip + limit - 1).execute()
            
            # Get total count
            count_result = self.supabase.table("workflows").select("id", count="exact").eq("user_id", user_id).execute()
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
    
    async def update_workflow(self, workflow_id: str, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a workflow"""
        try:
            # Check if workflow exists and belongs to user
            existing = await self.get_workflow(workflow_id, user_id)
            if not existing["success"]:
                return existing
            
            # Prepare update data
            filtered_update = {}
            allowed_fields = ["name", "description", "workflow_json", "status", "tags"]
            
            for field in allowed_fields:
                if field in update_data:
                    filtered_update[field] = update_data[field]
            
            # Update primitives count if workflow_json is updated
            if "workflow_json" in filtered_update:
                filtered_update["primitives_count"] = len(filtered_update["workflow_json"].get("primitives", []))
            
            if not filtered_update:
                return {"success": False, "error": "No valid fields to update"}
            
            # Update workflow
            result = self.supabase.table("workflows").update(filtered_update).eq("id", workflow_id).execute()
            
            if result.data:
                return {"success": True, "data": result.data[0]}
            else:
                return {"success": False, "error": "Failed to update workflow"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_workflow(self, workflow_id: str, user_id: str) -> Dict[str, Any]:
        """Delete a workflow"""
        try:
            # Check if workflow exists and belongs to user
            existing = await self.get_workflow(workflow_id, user_id)
            if not existing["success"]:
                return existing
            
            # Delete workflow (cascade will handle related records)
            result = self.supabase.table("workflows").delete().eq("id", workflow_id).execute()
            
            return {"success": True, "message": "Workflow deleted successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def increment_execution_count(self, workflow_id: str) -> Dict[str, Any]:
        """Increment workflow execution count"""
        try:
            # Get current workflow
            result = self.supabase.table("workflows").select("execution_count").eq("id", workflow_id).execute()
            
            if not result.data:
                return {"success": False, "error": "Workflow not found"}
            
            current_count = result.data[0]["execution_count"]
            
            # Update execution count and last executed timestamp
            update_result = self.supabase.table("workflows").update({
                "execution_count": current_count + 1,
                "last_executed_at": datetime.utcnow().isoformat()
            }).eq("id", workflow_id).execute()
            
            if update_result.data:
                return {"success": True, "data": update_result.data[0]}
            else:
                return {"success": False, "error": "Failed to update execution count"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_workflow_stats(self, user_id: str) -> Dict[str, Any]:
        """Get workflow statistics for a user"""
        try:
            # Get workflow counts by status
            total_result = self.supabase.table("workflows").select("id", count="exact").eq("user_id", user_id).execute()
            active_result = self.supabase.table("workflows").select("id", count="exact").eq("user_id", user_id).eq("status", "active").execute()
            draft_result = self.supabase.table("workflows").select("id", count="exact").eq("user_id", user_id).eq("status", "draft").execute()
            
            # Get total executions
            executions_result = self.supabase.table("workflow_executions").select("id", count="exact").eq("user_id", user_id).execute()
            
            # Get most recent workflows
            recent_result = self.supabase.table("workflows").select("id, name, status, updated_at").eq("user_id", user_id).order("updated_at", desc=True).limit(5).execute()
            
            return {
                "success": True,
                "data": {
                    "total_workflows": total_result.count or 0,
                    "active_workflows": active_result.count or 0,
                    "draft_workflows": draft_result.count or 0,
                    "total_executions": executions_result.count or 0,
                    "recent_workflows": recent_result.data or []
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global workflow CRUD instance
workflow_crud = WorkflowCRUD()
