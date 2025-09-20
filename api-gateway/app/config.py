"""
Configuration module for Flov7 API Gateway.
Handles application configuration and settings.
"""

from shared.config.settings import settings
from typing import Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)


class APIGatewayConfig:
    """Configuration class for API Gateway service"""
    
    def __init__(self):
        # Service configuration
        self.host = settings.API_GATEWAY_HOST
        self.port = settings.API_GATEWAY_PORT
        self.debug = settings.DEBUG
        self.log_level = settings.LOG_LEVEL
        
        # Supabase configuration
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_anon_key = settings.SUPABASE_ANON_KEY
        self.supabase_service_key = settings.SUPABASE_SERVICE_ROLE_KEY
        
        # Redis configuration
        self.redis_url = settings.REDIS_URL
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration values"""
        if not self.supabase_url:
            logger.warning("SUPABASE_URL not configured")
        
        if not self.supabase_anon_key:
            logger.warning("SUPABASE_ANON_KEY not configured")
        
        if not self.supabase_service_key:
            logger.warning("SUPABASE_SERVICE_ROLE_KEY not configured")
        
        if not self.redis_url:
            logger.warning("REDIS_URL not configured")


# Global configuration instance
config = APIGatewayConfig()
