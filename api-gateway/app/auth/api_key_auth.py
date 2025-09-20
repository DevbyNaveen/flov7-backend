"""
API Key Authentication Module for Flov7 API Gateway
Handles API key authentication for external integrations and service-to-service communication.
"""

from fastapi import HTTPException, Depends, status, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, UUID4
from typing import Optional, Dict, Any
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Key configuration
API_KEY_HEADER_NAME = "X-API-Key"
API_KEY_NAME_HEADER = "X-API-Key-Name"

# Security scheme
api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)

class APIKeyCreate(BaseModel):
    """API Key creation model"""
    name: str
    description: Optional[str] = None
    expires_in_days: Optional[int] = 365
    permissions: Optional[Dict[str, Any]] = None

class APIKeyResponse(BaseModel):
    """API Key response model"""
    id: UUID4
    name: str
    key_preview: str  # First 8 characters + asterisks
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    description: Optional[str]
    permissions: Optional[Dict[str, Any]]

class APIKeyManager:
    """API Key Authentication and Management"""

    def __init__(self):
        # In production, this would be stored in database
        # For now, using environment variables for demo
        self.api_keys = {}
        self._load_existing_keys()

    def _load_existing_keys(self):
        """Load existing API keys from environment or database"""
        # This is a placeholder - in production, load from database
        existing_keys = os.getenv("API_KEYS", "")
        if existing_keys:
            # Parse and load existing keys
            pass

    async def create_api_key(self, key_data: APIKeyCreate) -> Dict[str, Any]:
        """Create a new API key"""
        try:
            import uuid
            from supabase import create_client

            # Generate secure API key
            raw_key = secrets.token_urlsafe(32)
            key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

            # Calculate expiration
            expires_at = None
            if key_data.expires_in_days:
                expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)

            # Create key record
            key_record = {
                "id": str(uuid.uuid4()),
                "name": key_data.name,
                "key_hash": key_hash,
                "created_at": datetime.utcnow(),
                "expires_at": expires_at,
                "is_active": True,
                "description": key_data.description,
                "permissions": key_data.permissions or {},
                "last_used": None,
                "usage_count": 0
            }

            # Store in memory (in production, store in database)
            self.api_keys[key_hash] = key_record

            return {
                "id": key_record["id"],
                "name": key_record["name"],
                "api_key": raw_key,  # Only shown once during creation
                "key_preview": raw_key[:8] + "*" * 24,
                "created_at": key_record["created_at"],
                "expires_at": expires_at,
                "is_active": True,
                "description": key_record["description"],
                "permissions": key_record["permissions"],
                "message": "API key created successfully. Store the key securely - it won't be shown again."
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create API key: {str(e)}"
            )

    async def authenticate_api_key(self, request: Request) -> Dict[str, Any]:
        """Authenticate request using API key"""
        # Get API key from header
        api_key = request.headers.get(API_KEY_HEADER_NAME)

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required",
                headers={"WWW-Authenticate": "ApiKey"}
            )

        # Hash the provided key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Look up key
        key_record = self.api_keys.get(key_hash)

        if not key_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )

        # Check if key is active
        if not key_record.get("is_active", False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key is inactive"
            )

        # Check expiration
        if key_record.get("expires_at") and datetime.utcnow() > key_record["expires_at"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired"
            )

        # Update usage statistics
        key_record["last_used"] = datetime.utcnow()
        key_record["usage_count"] = key_record.get("usage_count", 0) + 1

        return {
            "id": key_record["id"],
            "name": key_record["name"],
            "permissions": key_record.get("permissions", {}),
            "authenticated": True
        }

    async def get_api_keys(self, include_inactive: bool = False) -> list:
        """Get list of API keys"""
        keys = []
        for key_hash, key_record in self.api_keys.items():
            if not include_inactive and not key_record.get("is_active", False):
                continue

            keys.append({
                "id": key_record["id"],
                "name": key_record["name"],
                "key_preview": key_record.get("key_preview", "********"),
                "created_at": key_record["created_at"],
                "expires_at": key_record["expires_at"],
                "is_active": key_record.get("is_active", False),
                "description": key_record.get("description"),
                "last_used": key_record.get("last_used"),
                "usage_count": key_record.get("usage_count", 0)
            })

        return keys

    async def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key"""
        for key_hash, key_record in self.api_keys.items():
            if key_record["id"] == key_id:
                key_record["is_active"] = False
                return True

        return False

    async def validate_permissions(self, api_key_data: Dict[str, Any], required_permissions: list) -> bool:
        """Validate if API key has required permissions"""
        key_permissions = api_key_data.get("permissions", {})

        for permission in required_permissions:
            if not key_permissions.get(permission, False):
                return False

        return True

# Dependency for API key authentication
async def get_api_key_data(request: Request) -> Dict[str, Any]:
    """Dependency to get authenticated API key data"""
    api_key_manager = APIKeyManager()
    return await api_key_manager.authenticate_api_key(request)

# Dependency for API key with specific permissions
def require_api_permissions(required_permissions: list):
    """Create dependency that requires specific API permissions"""
    async def permission_dependency(api_key_data: Dict[str, Any] = Depends(get_api_key_data)):
        api_key_manager = APIKeyManager()
        has_permissions = await api_key_manager.validate_permissions(api_key_data, required_permissions)

        if not has_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API key lacks required permissions: {', '.join(required_permissions)}"
            )

        return api_key_data

    return permission_dependency

# Global API key manager instance
api_key_manager = APIKeyManager()
