"""
Authentication Router for Flov7 API Gateway
Provides authentication endpoints for user registration, login, and API key management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from app.auth.supabase_auth import supabase_auth, UserCreate, UserLogin, Token
from app.auth.api_key_auth import api_key_manager, APIKeyCreate, get_api_key_data, require_api_permissions

# Create router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        422: {"description": "Validation Error"}
    }
)

# User Authentication Endpoints
@router.post("/register", response_model=Dict[str, Any])
async def register_user(user_data: UserCreate):
    """Register a new user account"""
    return await supabase_auth.register_user(user_data)

@router.post("/login", response_model=Token)
async def login_user(user_data: UserLogin):
    """Authenticate user and return access token"""
    return await supabase_auth.authenticate_user(user_data)

@router.post("/logout")
async def logout_user(current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)):
    """Logout current user"""
    return await supabase_auth.logout_user()

@router.get("/me")
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)):
    """Get current user profile information"""
    return {
        "user": current_user,
        "status": "authenticated"
    }

@router.get("/verify")
async def verify_token(current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)):
    """Verify JWT token validity"""
    return {
        "valid": True,
        "user": current_user
    }

# API Key Management Endpoints
@router.post("/api-keys", response_model=Dict[str, Any])
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Create a new API key for the authenticated user"""
    return await api_key_manager.create_api_key(key_data)

@router.get("/api-keys")
async def list_api_keys(
    include_inactive: bool = False,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """List all API keys for the authenticated user"""
    return await api_key_manager.get_api_keys(include_inactive)

@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: Dict[str, Any] = Depends(supabase_auth.get_current_user)
):
    """Revoke an API key"""
    success = await api_key_manager.revoke_api_key(key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    return {"message": "API key revoked successfully"}

# API Key Authentication Test Endpoints
@router.get("/test/api-key")
async def test_api_key_auth(api_key_data: Dict[str, Any] = Depends(get_api_key_data)):
    """Test endpoint that requires API key authentication"""
    return {
        "authenticated": True,
        "api_key": {
            "id": api_key_data["id"],
            "name": api_key_data["name"]
        },
        "message": "API key authentication successful"
    }

@router.get("/test/permissions")
async def test_permissions(
    api_key_data: Dict[str, Any] = Depends(require_api_permissions(["read", "write"]))
):
    """Test endpoint that requires specific API permissions"""
    return {
        "authenticated": True,
        "permissions_valid": True,
        "api_key": {
            "id": api_key_data["id"],
            "name": api_key_data["name"],
            "permissions": api_key_data["permissions"]
        }
    }

# Health check for auth services
@router.get("/health")
async def auth_health_check():
    """Health check for authentication services"""
    return {
        "status": "healthy",
        "service": "authentication",
        "features": [
            "supabase_auth",
            "jwt_tokens",
            "api_keys",
            "permissions"
        ]
    }
