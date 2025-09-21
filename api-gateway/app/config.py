"""
Configuration module for Flov7 API Gateway.
Handles application configuration and settings.
"""

from shared.config.settings import settings
from typing import Optional
import logging
import httpx
from urllib.parse import urljoin

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
        
        # AI Service configuration
        self.ai_service_url = f"http://{settings.AI_SERVICE_HOST}:{settings.AI_SERVICE_PORT}"
        self.ai_service_timeout = 30  # seconds
        
        # Workflow Service configuration
        self.workflow_service_url = f"http://{settings.WORKFLOW_SERVICE_HOST}:{settings.WORKFLOW_SERVICE_PORT}"
        self.workflow_service_timeout = 30  # seconds
        
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
    
    def get_ai_service_client(self) -> httpx.AsyncClient:
        """Get configured HTTP client for AI service communication"""
        return httpx.AsyncClient(
            base_url=self.ai_service_url,
            timeout=httpx.Timeout(self.ai_service_timeout),
            headers={"Content-Type": "application/json"}
        )
    
    def get_workflow_service_client(self) -> httpx.AsyncClient:
        """Get configured HTTP client for workflow service communication"""
        return httpx.AsyncClient(
            base_url=self.workflow_service_url,
            timeout=httpx.Timeout(self.workflow_service_timeout),
            headers={"Content-Type": "application/json"}
        )


# Global configuration instance
config = APIGatewayConfig()
