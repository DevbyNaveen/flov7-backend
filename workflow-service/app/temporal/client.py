"""
Temporal client for Flov7 workflow service.
Handles connection to Temporal server for workflow orchestration.
"""

from temporalio.client import Client
from shared.config.settings import settings
from typing import Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)


class TemporalClientManager:
    """Temporal client connection manager"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Temporal client connection"""
        try:
            if settings.TEMPORAL_HOST:
                # In a real implementation, we would connect to Temporal
                # For now, we'll just log that initialization is attempted
                logger.info(f"Temporal client initialization attempted with host: {settings.TEMPORAL_HOST}")
                # self.client = await Client.connect(settings.TEMPORAL_HOST, namespace=settings.TEMPORAL_NAMESPACE)
            else:
                logger.warning("Temporal host not configured. Temporal features will be disabled.")
        except Exception as e:
            logger.error(f"Failed to initialize Temporal client: {str(e)}")
            self.client = None
    
    def get_client(self) -> Optional[Client]:
        """Get Temporal client instance"""
        return self.client
    
    async def connect(self) -> bool:
        """
        Connect to Temporal server
        
        Returns:
            Boolean indicating connection success
        """
        try:
            if not settings.TEMPORAL_HOST:
                logger.warning("Cannot connect to Temporal: host not configured")
                return False
            
            # Connect to Temporal server
            self.client = await Client.connect(
                settings.TEMPORAL_HOST, 
                namespace=settings.TEMPORAL_NAMESPACE
            )
            
            logger.info(f"Connected to Temporal server at {settings.TEMPORAL_HOST}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Temporal server: {str(e)}")
            self.client = None
            return False


# Global Temporal client manager instance
temporal_client_manager = TemporalClientManager()

# Global Temporal client instance
temporal_client = temporal_client_manager.get_client()
