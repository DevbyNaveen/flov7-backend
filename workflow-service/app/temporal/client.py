"""
Temporal client for Flov7 workflow service.
Handles connection to Temporal server for workflow orchestration.
"""

from temporalio.client import Client
from shared.config.settings import settings
from typing import Optional
import logging
import asyncio

# Configure logging
logger = logging.getLogger(__name__)


class TemporalClientManager:
    """Temporal client connection manager with proper async initialization"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._connection_attempted = False
        self._connection_lock = asyncio.Lock()
        self._initialization_task: Optional[asyncio.Task] = None
    
    async def _initialize_client(self):
        """Initialize Temporal client connection asynchronously with proper error handling"""
        async with self._connection_lock:
            if self._connection_attempted:
                return
                
            self._connection_attempted = True
            
            try:
                # Check if Temporal configuration is available
                temporal_host = getattr(settings, 'TEMPORAL_HOST', None)
                temporal_namespace = getattr(settings, 'TEMPORAL_NAMESPACE', 'default')
                
                if temporal_host:
                    logger.info(f"Attempting to connect to Temporal server at {temporal_host}")
                    
                    # Set connection timeout
                    connection_timeout = 10.0  # 10 seconds timeout
                    
                    # Connect to Temporal with timeout
                    self.client = await asyncio.wait_for(
                        Client.connect(
                            temporal_host, 
                            namespace=temporal_namespace
                        ),
                        timeout=connection_timeout
                    )
                    
                    # Test the connection
                    await self.client.workflow_service.get_system_info()
                    logger.info("Successfully connected to Temporal server")
                    
                else:
                    logger.warning("Temporal host not configured. Temporal features will be disabled.")
                    
            except asyncio.TimeoutError:
                logger.warning("Temporal connection timed out. Using local fallback execution.")
                self.client = None
            except Exception as e:
                logger.warning(f"Failed to initialize Temporal client: {str(e)}")
                logger.info("Workflow service will use local fallback execution")
                self.client = None
    
    def get_client(self) -> Optional[Client]:
        """Get Temporal client instance (synchronous)"""
        return self.client
    
    async def connect(self) -> bool:
        """
        Connect to Temporal server
        
        Returns:
            Boolean indicating connection success
        """
        await self._initialize_client()
        return self.client is not None
    
    async def get_client_async(self) -> Optional[Client]:
        """Get Temporal client instance, initializing if needed"""
        if not self._connection_attempted:
            await self._initialize_client()
        return self.client
    
    async def is_connected(self) -> bool:
        """
        Check if Temporal client is connected and healthy
        
        Returns:
            Boolean indicating connection health
        """
        if not self.client:
            return False
            
        try:
            # Test connection health
            await self.client.workflow_service.get_system_info()
            return True
        except Exception as e:
            logger.warning(f"Temporal connection health check failed: {str(e)}")
            return False
    
    async def close(self):
        """Close Temporal client connection"""
        if self.client:
            try:
                await self.client.close()
                logger.info("Temporal client connection closed")
            except Exception as e:
                logger.error(f"Error closing Temporal client: {str(e)}")
            finally:
                self.client = None
                self._connection_attempted = False


# Global Temporal client manager instance
temporal_client_manager = TemporalClientManager()

# Function to get temporal client (async)
async def get_temporal_client() -> Optional[Client]:
    """Get the temporal client instance"""
    return await temporal_client_manager.get_client_async()

# Function to initialize temporal client on startup
async def initialize_temporal_client():
    """Initialize Temporal client on application startup"""
    logger.info("Initializing Temporal client...")
    success = await temporal_client_manager.connect()
    if success:
        logger.info("Temporal client initialized successfully")
    else:
        logger.info("Temporal client initialization failed, using local fallback")
    return success

# Function to close temporal client on shutdown
async def close_temporal_client():
    """Close Temporal client on application shutdown"""
    logger.info("Closing Temporal client...")
    await temporal_client_manager.close()
