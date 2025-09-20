"""
Configuration module for Flov7 AI Service.
Handles application configuration and settings.
"""

from shared.config.settings import settings
from typing import Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)


class AIServiceConfig:
    """Configuration class for AI Service"""
    
    def __init__(self):
        # Service configuration
        self.host = settings.AI_SERVICE_HOST
        self.port = settings.AI_SERVICE_PORT
        self.debug = settings.DEBUG
        self.log_level = settings.LOG_LEVEL
        
        # OpenAI configuration
        self.openai_api_key = settings.OPENAI_API_KEY
        
        # Supabase configuration
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_service_key = settings.SUPABASE_SERVICE_ROLE_KEY
        
        # Redis configuration
        self.redis_url = settings.REDIS_URL
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration values"""
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not configured - AI features will be disabled")
        
        if not self.supabase_url:
            logger.warning("SUPABASE_URL not configured")
        
        if not self.supabase_service_key:
            logger.warning("SUPABASE_SERVICE_ROLE_KEY not configured")
        
        if not self.redis_url:
            logger.warning("REDIS_URL not configured")


# Global configuration instance
config = AIServiceConfig()
