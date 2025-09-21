"""
Real-time subscriptions endpoints for Flov7 API Gateway
Handles WebSocket connections and Supabase real-time subscriptions.
"""

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List, Optional
from uuid import UUID
import json
import asyncio
import logging
from datetime import datetime

from app.auth.supabase_auth import supabase_auth
from shared.config.database import db_manager
from shared.crud.notifications import notification_crud

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/realtime",
    tags=["Real-time"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        422: {"description": "Validation Error"}
    }
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, channel: str):
        """Connect a WebSocket to a specific channel"""
        await websocket.accept()
        
        # Add to channel connections
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
        
        # Add to user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)
        
        logger.info(f"User {user_id} connected to channel {channel}")
    
    def disconnect(self, websocket: WebSocket, user_id: str, channel: str):
        """Disconnect a WebSocket from a channel"""
        # Remove from channel connections
        if channel in self.active_connections:
            if websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)
            if not self.active_connections[channel]:
                del self.active_connections[channel]
        
        # Remove from user connections
        if user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(f"User {user_id} disconnected from channel {channel}")
    
    async def send_to_channel(self, channel: str, message: dict):
        """Send message to all connections in a channel"""
        if channel in self.active_connections:
            disconnected = []
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.active_connections[channel].remove(connection)
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to all connections for a specific user"""
        if user_id in self.user_connections:
            disconnected = []
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.user_connections[user_id].remove(connection)

# Global connection manager
manager = ConnectionManager()

# WebSocket endpoint for workflow execution updates
@router.websocket("/ws/workflows/{user_id}")
async def workflow_websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for workflow execution updates"""
    channel = f"workflows:{user_id}"
    
    try:
        await manager.connect(websocket, user_id, channel)
        
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection",
            "status": "connected",
            "channel": channel,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle ping/pong for connection health
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                }))
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        manager.disconnect(websocket, user_id, channel)

# WebSocket endpoint for notifications
@router.websocket("/ws/notifications/{user_id}")
async def notifications_websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time notifications"""
    channel = f"notifications:{user_id}"
    
    try:
        await manager.connect(websocket, user_id, channel)
        
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection",
            "status": "connected",
            "channel": channel,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle ping/pong for connection health
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                }))
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        manager.disconnect(websocket, user_id, channel)

# REST endpoints for triggering real-time updates
@router.post("/notify/workflow-status")
async def notify_workflow_status(
    workflow_id: str,
    execution_id: str,
    status: str,
    user_id: str,
    message: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None
):
    """Send workflow status update to connected clients"""
    try:
        notification = {
            "type": "workflow_status",
            "workflow_id": workflow_id,
            "execution_id": execution_id,
            "status": status,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to user's workflow channel
        await manager.send_to_user(user_id, notification)
        
        # Also create a database notification for persistent storage using notification_crud
        await notification_crud.create_notification({
            "user_id": user_id,
            "type": "workflow_status",
            "title": f"Workflow {status}",
            "message": message or f"Workflow execution {status}",
            "data": {
                "workflow_id": workflow_id,
                "execution_id": execution_id,
                "status": status
            }
        })
        
        return {
            "success": True,
            "message": "Notification sent successfully"
        }
        
    except Exception as e:
        logger.error(f"Error sending workflow notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending notification: {str(e)}"
        )

@router.post("/notify/user-notification")
async def send_user_notification(
    user_id: str,
    notification_type: str,
    title: str,
    message: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
    persist: bool = True
):
    """Send a notification to a specific user"""
    try:
        notification = {
            "type": "notification",
            "notification_type": notification_type,
            "title": title,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send real-time notification
        await manager.send_to_user(user_id, notification)
        
        # Persist to database if requested using notification_crud
        if persist:
            await notification_crud.create_notification({
                "user_id": user_id,
                "type": notification_type,
                "title": title,
                "message": message,
                "data": data or {}
            })
        
        return {
            "success": True,
            "message": "Notification sent successfully"
        }
        
    except Exception as e:
        logger.error(f"Error sending user notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending notification: {str(e)}"
        )

@router.post("/broadcast/system-announcement")
async def broadcast_system_announcement(
    title: str,
    message: str,
    announcement_type: str = "info",
    data: Optional[Dict[str, Any]] = None,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Broadcast system announcement to all connected users (admin only)"""
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        announcement = {
            "type": "system_announcement",
            "announcement_type": announcement_type,
            "title": title,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to all connected users
        for user_id in manager.user_connections:
            await manager.send_to_user(user_id, announcement)
        
        # Create system announcement notification for all users using notification_crud
        result = await notification_crud.create_system_announcement(
            title=title,
            message=message,
            data=data or {}
        )
        
        return {
            "success": True,
            "message": f"System announcement sent to {len(manager.user_connections)} connected users",
            "connected_users": len(manager.user_connections)
        }
        
    except Exception as e:
        logger.error(f"Error broadcasting system announcement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error broadcasting announcement: {str(e)}"
        )

# Subscription management endpoints
@router.get("/subscriptions/status")
async def get_subscription_status(
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Get current user's real-time subscription status"""
    user_id = current_user["id"]
    
    # Check if user has active WebSocket connections
    active_connections = len(manager.user_connections.get(user_id, []))
    
    # Get channels the user is subscribed to
    subscribed_channels = []
    for channel, connections in manager.active_connections.items():
        user_connections = manager.user_connections.get(user_id, [])
        if any(conn in connections for conn in user_connections):
            subscribed_channels.append(channel)
    
    return {
        "user_id": user_id,
        "active_connections": active_connections,
        "subscribed_channels": subscribed_channels,
        "status": "connected" if active_connections > 0 else "disconnected"
    }

@router.get("/admin/connections")
async def get_all_connections(
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Get all active WebSocket connections (admin only)"""
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get connection statistics
    total_connections = sum(len(connections) for connections in manager.user_connections.values())
    total_users = len(manager.user_connections)
    total_channels = len(manager.active_connections)
    
    # Get detailed connection info
    user_stats = {}
    for user_id, connections in manager.user_connections.items():
        user_stats[user_id] = {
            "connection_count": len(connections),
            "channels": []
        }
        
        # Find channels for this user
        for channel, channel_connections in manager.active_connections.items():
            if any(conn in channel_connections for conn in connections):
                user_stats[user_id]["channels"].append(channel)
    
    return {
        "total_connections": total_connections,
        "total_users": total_users,
        "total_channels": total_channels,
        "user_stats": user_stats,
        "channels": list(manager.active_connections.keys())
    }

# Health check
@router.get("/health")
async def realtime_health_check():
    """Health check for real-time endpoints"""
    total_connections = sum(len(connections) for connections in manager.user_connections.values())
    
    return {
        "status": "healthy",
        "service": "realtime",
        "active_connections": total_connections,
        "active_users": len(manager.user_connections),
        "active_channels": len(manager.active_connections),
        "features": [
            "websocket_connections",
            "workflow_updates",
            "notifications",
            "system_announcements",
            "connection_management"
        ]
    }
