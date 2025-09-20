"""
Supabase Authentication Module for Flov7 API Gateway
Handles user authentication, registration, and session management using Supabase Auth.
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import os
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]

class SupabaseAuth:
    """Supabase Authentication Handler"""

    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        self.service_supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

    async def register_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """Register a new user with Supabase Auth"""
        try:
            response = self.supabase.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "full_name": user_data.full_name,
                        "created_at": datetime.utcnow().isoformat()
                    }
                }
            })

            if response.user:
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "full_name": user_data.full_name,
                        "created_at": response.user.created_at
                    },
                    "message": "User registered successfully. Please check your email for verification."
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration failed"
                )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration error: {str(e)}"
            )

    async def authenticate_user(self, user_data: UserLogin) -> Dict[str, Any]:
        """Authenticate user with Supabase Auth"""
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": user_data.email,
                "password": user_data.password
            })

            if response.user and response.session:
                # Create JWT token
                access_token = self._create_access_token({
                    "sub": response.user.id,
                    "email": response.user.email,
                    "full_name": response.user.user_metadata.get("full_name")
                })

                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "expires_in": JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "full_name": response.user.user_metadata.get("full_name"),
                        "created_at": response.user.created_at
                    }
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication error: {str(e)}"
            )

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Get current authenticated user from JWT token"""
        try:
            payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("sub")

            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )

            # Get user from Supabase
            response = self.service_supabase.auth.admin.get_user_by_id(user_id)

            return {
                "id": response.user.id,
                "email": response.user.email,
                "full_name": response.user.user_metadata.get("full_name"),
                "created_at": response.user.created_at
            }

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication error: {str(e)}"
            )

    async def logout_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Logout user by invalidating session"""
        try:
            # Sign out from Supabase
            self.supabase.auth.sign_out()
            return {"message": "Successfully logged out"}

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Logout error: {str(e)}"
            )

    def _create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def _get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)

# Global auth instance
supabase_auth = SupabaseAuth()
