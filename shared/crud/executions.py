"""
CRUD operations for workflow executions table.
Provides database operations for execution tracking and management.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from supabase import Client

from shared.config.database import db_manager


class WorkflowExecutionCRUD:
    """CRUD operations for workflow executions"""
    
    def __init__(self):
        self.supabase = db_manager.get_client()
        self.service_supabase = db_manager.get_service_client()
    
    async def create_execution(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow execution record"""
        try:
            insert_data = {
                "workflow_id": execution_data["workflow_id"],
                "user_id": execution_data["user_id"],
                "status": execution_data.get("status", "pending"),
                "input_data": execution_data.get("input_data", {}),
                "temporal_workflow_id": execution_data.get("temporal_workflow_id"),
                "started_at": execution_data.get("started_at", datetime.utcnow().isoformat())
            }
            
            result = self.supabase.table("workflow_executions").insert(insert_data).execute()
            
            if result.data:
                return {"success": True, "data": result.data[0]}
            else:
                return {"success": False, "error": "Failed to create execution record"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_execution(self, execution_id: str, user_id: str) -> Dict[str, Any]:
        """Get execution by ID"""
        try:
            result = self.supabase.table("workflow_executions").select("*").eq("id", execution_id).eq("user_id", user_id).execute()
            
            if result.data:
                return {"success": True, "data": result.data[0]}
            else:
                return {"success": False, "error": "Execution not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_executions(
        self, 
        user_id: str,
        workflow_id: Optional[str] = None,
        skip: int = 0, 
        limit: int = 20,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """List executions with pagination and filtering"""
        try:
            # Build query
            query = self.supabase.table("workflow_executions").select("*").eq("user_id", user_id)
            
            # Apply filters
            if workflow_id:
                query = query.eq("workflow_id", workflow_id)
            if status:
                query = query.eq("status", status)
            
            # Apply pagination and ordering
            result = query.order("created_at", desc=True).range(skip, skip + limit - 1).execute()
            
            # Get total count
            count_query = self.supabase.table("workflow_executions").select("id", count="exact").eq("user_id", user_id)
            if workflow_id:
                count_query = count_query.eq("workflow_id", workflow_id)
            if status:
                count_query = count_query.eq("status", status)
            
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
    
    async def update_execution_status(
        self, 
        execution_id: str, 
        status: str,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        execution_time_seconds: Optional[float] = None,
        cost_usd: Optional[float] = None
    ) -> Dict[str, Any]:
        """Update execution status and results"""
        try:
            # Prepare update data
            update_data = {"status": status}
            
            if output_data is not None:
                update_data["output_data"] = output_data
            if error_message is not None:
                update_data["error_message"] = error_message
            if execution_time_seconds is not None:
                update_data["execution_time_seconds"] = execution_time_seconds
            if cost_usd is not None:
                update_data["cost_usd"] = cost_usd
            
            # Set completion timestamp for completed/failed executions
            if status in ["completed", "failed"]:
                update_data["completed_at"] = datetime.utcnow().isoformat()
            
            # Update execution
            result = self.supabase.table("workflow_executions").update(update_data).eq("id", execution_id).execute()
            
            if result.data:
                return {"success": True, "data": result.data[0]}
            else:
                return {"success": False, "error": "Failed to update execution"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_execution_stats(self, user_id: str, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """Get execution statistics"""
        try:
            # Build base query
            base_query = self.supabase.table("workflow_executions").eq("user_id", user_id)
            if workflow_id:
                base_query = base_query.eq("workflow_id", workflow_id)
            
            # Get counts by status
            total_result = base_query.select("id", count="exact").execute()
            pending_result = base_query.select("id", count="exact").eq("status", "pending").execute()
            running_result = base_query.select("id", count="exact").eq("status", "running").execute()
            completed_result = base_query.select("id", count="exact").eq("status", "completed").execute()
            failed_result = base_query.select("id", count="exact").eq("status", "failed").execute()
            
            # Get recent executions
            recent_result = base_query.select("*").order("created_at", desc=True).limit(10).execute()
            
            # Calculate success rate
            total_count = total_result.count or 0
            completed_count = completed_result.count or 0
            failed_count = failed_result.count or 0
            finished_count = completed_count + failed_count
            success_rate = (completed_count / finished_count * 100) if finished_count > 0 else 0
            
            return {
                "success": True,
                "data": {
                    "total_executions": total_count,
                    "pending_executions": pending_result.count or 0,
                    "running_executions": running_result.count or 0,
                    "completed_executions": completed_count,
                    "failed_executions": failed_count,
                    "success_rate": round(success_rate, 2),
                    "recent_executions": recent_result.data or []
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_execution_by_temporal_id(self, temporal_workflow_id: str) -> Dict[str, Any]:
        """Get execution by Temporal workflow ID"""
        try:
            result = self.supabase.table("workflow_executions").select("*").eq("temporal_workflow_id", temporal_workflow_id).execute()
            
            if result.data:
                return {"success": True, "data": result.data[0]}
            else:
                return {"success": False, "error": "Execution not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_execution(self, execution_id: str, user_id: str) -> Dict[str, Any]:
        """Delete an execution record"""
        try:
            # Check if execution exists and belongs to user
            existing = await self.get_execution(execution_id, user_id)
            if not existing["success"]:
                return existing
            
            # Delete execution
            result = self.supabase.table("workflow_executions").delete().eq("id", execution_id).execute()
            
            return {"success": True, "message": "Execution deleted successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Admin functions
    async def list_all_executions(
        self, 
        skip: int = 0, 
        limit: int = 50,
        status: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """List all executions (admin only)"""
        try:
            # Build query
            query = self.service_supabase.table("workflow_executions").select("*, workflows(name), users(email)")
            
            # Apply filters
            if status:
                query = query.eq("status", status)
            if user_id:
                query = query.eq("user_id", user_id)
            
            # Apply pagination and ordering
            result = query.order("created_at", desc=True).range(skip, skip + limit - 1).execute()
            
            # Get total count
            count_query = self.service_supabase.table("workflow_executions").select("id", count="exact")
            if status:
                count_query = count_query.eq("status", status)
            if user_id:
                count_query = count_query.eq("user_id", user_id)
            
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
    
    async def get_system_execution_stats(self) -> Dict[str, Any]:
        """Get system-wide execution statistics (admin only)"""
        try:
            # Get counts by status
            total_result = self.service_supabase.table("workflow_executions").select("id", count="exact").execute()
            pending_result = self.service_supabase.table("workflow_executions").select("id", count="exact").eq("status", "pending").execute()
            running_result = self.service_supabase.table("workflow_executions").select("id", count="exact").eq("status", "running").execute()
            completed_result = self.service_supabase.table("workflow_executions").select("id", count="exact").eq("status", "completed").execute()
            failed_result = self.service_supabase.table("workflow_executions").select("id", count="exact").eq("status", "failed").execute()
            
            # Get executions from last 24 hours
            yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
            recent_result = self.service_supabase.table("workflow_executions").select("id", count="exact").gte("created_at", yesterday).execute()
            
            # Calculate success rate
            total_count = total_result.count or 0
            completed_count = completed_result.count or 0
            failed_count = failed_result.count or 0
            finished_count = completed_count + failed_count
            success_rate = (completed_count / finished_count * 100) if finished_count > 0 else 0
            
            return {
                "success": True,
                "data": {
                    "total_executions": total_count,
                    "pending_executions": pending_result.count or 0,
                    "running_executions": running_result.count or 0,
                    "completed_executions": completed_count,
                    "failed_executions": failed_count,
                    "success_rate": round(success_rate, 2),
                    "executions_last_24h": recent_result.count or 0
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global execution CRUD instance
execution_crud = WorkflowExecutionCRUD()
