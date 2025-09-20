"""
Global settings configuration for Flov7 platform.
Environment-based configuration management.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Global settings configuration"""
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # AI Service Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Workflow Service Configuration
    TEMPORAL_HOST: str = os.getenv("TEMPORAL_HOST", "localhost:7233")
    TEMPORAL_NAMESPACE: str = os.getenv("TEMPORAL_NAMESPACE", "default")
    
    # Infrastructure Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # API Gateway Settings
    API_GATEWAY_PORT: int = int(os.getenv("API_GATEWAY_PORT", "8000"))
    API_GATEWAY_HOST: str = os.getenv("API_GATEWAY_HOST", "0.0.0.0")
    
    # AI Service Settings
    AI_SERVICE_PORT: int = int(os.getenv("AI_SERVICE_PORT", "8001"))
    AI_SERVICE_HOST: str = os.getenv("AI_SERVICE_HOST", "0.0.0.0")
    
    # Workflow Service Settings
    WORKFLOW_SERVICE_PORT: int = int(os.getenv("WORKFLOW_SERVICE_PORT", "8002"))
    WORKFLOW_SERVICE_HOST: str = os.getenv("WORKFLOW_SERVICE_HOST", "0.0.0.0")
    
    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


# Global settings instance
settings = Settings()
