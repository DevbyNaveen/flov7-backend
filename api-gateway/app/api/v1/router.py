"""
API v1 router for Flov7 API Gateway.
Main router that includes all v1 endpoints.
"""

from fastapi import APIRouter
from app.api.v1.auth_router import router as auth_router

# Create main v1 router
router = APIRouter(
    prefix="/api/v1"
)

# Include all sub-routers
router.include_router(auth_router)
