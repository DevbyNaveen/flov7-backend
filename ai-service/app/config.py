"""
Configuration module for Flov7 AI Service.
Handles application configuration and settings.
"""

from shared.config.settings import settings
from shared.config.database import db_manager
from typing import Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)


class AIServiceConfig:
    """Configuration class for AI Service"""
    
    def __init__(self):
        # Service configuration
        self.host = getattr(settings, 'AI_SERVICE_HOST', '0.0.0.0')
        self.port = getattr(settings, 'AI_SERVICE_PORT', 8001)
        self.debug = getattr(settings, 'DEBUG', False)
        self.log_level = getattr(settings, 'LOG_LEVEL', 'INFO')
        
        # OpenAI configuration
        self.openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.openai_model = getattr(settings, 'OPENAI_MODEL', 'gpt-4')
        self.openai_max_tokens = getattr(settings, 'OPENAI_MAX_TOKENS', 4000)
        
        # Supabase configuration
        self.supabase_url = getattr(settings, 'SUPABASE_URL', None)
        self.supabase_service_key = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', None)
        self.supabase_anon_key = getattr(settings, 'SUPABASE_ANON_KEY', None)
        
        # Redis configuration
        self.redis_url = getattr(settings, 'REDIS_URL', None)
        
        # Database manager
        self.db_manager = db_manager
        
        # AI Service specific settings
        self.enable_database_persistence = True
        self.enable_advanced_prompts = True
        self.max_workflow_complexity = 20  # Max number of nodes
        self.workflow_generation_timeout = 60  # seconds
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration values"""
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not configured - AI features will be disabled")
            self.enable_advanced_prompts = False
        
        if not self.supabase_url:
            logger.warning("SUPABASE_URL not configured - Database persistence disabled")
            self.enable_database_persistence = False
        
        if not self.supabase_service_key:
            logger.warning("SUPABASE_SERVICE_ROLE_KEY not configured - Database persistence disabled")
            self.enable_database_persistence = False
        
        if not self.redis_url:
            logger.warning("REDIS_URL not configured - Caching disabled")
    
    def get_database_client(self):
        """Get database client for AI service operations"""
        if not self.enable_database_persistence:
            raise ValueError("Database persistence is disabled")
        return self.db_manager.get_service_client()


# Global configuration instance
config = AIServiceConfig()
