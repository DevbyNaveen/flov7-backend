"""
API v1 router for Flov7 API Gateway.
Main router that includes all v1 endpoints.
"""

from fastapi import APIRouter
from app.api.v1.auth_router import router as auth_router
from app.api.v1.endpoints.workflows import router as workflows_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.realtime import router as realtime_router
from shared.config.database import db_manager

# Create main v1 router
router = APIRouter(
    prefix="/api/v1"
)

# Include all sub-routers
router.include_router(auth_router)
router.include_router(workflows_router)
router.include_router(users_router)
router.include_router(realtime_router)


@router.get("/health/database")
async def database_health_check():
    """Health check for database connectivity"""
    try:
        health_status = db_manager.health_check()
        
        if health_status["database_connection"]:
            return {
                "status": "healthy",
                "service": "database",
                "details": health_status
            }
        else:
            return {
                "status": "unhealthy",
                "service": "database",
                "error": health_status.get("error", "Unknown database error"),
                "details": health_status
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "database",
            "error": str(e)
        }
