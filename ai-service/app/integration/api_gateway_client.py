"""
API Gateway integration client for AI service.
Handles communication between AI service and API Gateway.
"""

import httpx
import asyncio
from typing import Dict, Any, Optional
import logging
from app.config import config

# Configure logging
logger = logging.getLogger(__name__)


class APIGatewayClient:
    """Client for communicating with API Gateway"""
    
    def __init__(self):
        self.base_url = self._get_api_gateway_url()
        self.timeout = 30.0
        self.client: Optional[httpx.AsyncClient] = None
    
    def _get_api_gateway_url(self) -> str:
        """Get API Gateway URL from configuration"""
        host = getattr(config, 'api_gateway_host', 'localhost')
        port = getattr(config, 'api_gateway_port', 8000)
        return f"http://{host}:{port}"
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            await self.client.aclose()
    
    async def notify_workflow_generated(self, workflow_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Notify API Gateway that a workflow has been generated
        
        Args:
            workflow_data: Generated workflow data
            user_id: ID of the user who requested the workflow
            
        Returns:
            Response from API Gateway
        """
        try:
            if not self.client:
                async with APIGatewayClient() as client:
                    return await client.notify_workflow_generated(workflow_data, user_id)
            
            payload = {
                "event": "workflow_generated",
                "user_id": user_id,
                "workflow_data": workflow_data,
                "source": "ai_service"
            }
            
            response = await self.client.post(
                "/api/v1/events/workflow-generated",
                json=payload
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                logger.warning(f"API Gateway notification failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error notifying API Gateway: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get user context from API Gateway for enhanced workflow generation
        
        Args:
            user_id: ID of the user
            
        Returns:
            User context data
        """
        try:
            if not self.client:
                async with APIGatewayClient() as client:
                    return await client.get_user_context(user_id)
            
            response = await self.client.get(
                f"/api/v1/users/{user_id}/context"
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                logger.warning(f"Failed to get user context: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting user context: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def register_ai_service(self) -> Dict[str, Any]:
        """
        Register AI service with API Gateway
        
        Returns:
            Registration response
        """
        try:
            if not self.client:
                async with APIGatewayClient() as client:
                    return await client.register_ai_service()
            
            payload = {
                "service_name": "ai-service",
                "service_url": f"http://localhost:{config.port}",
                "health_endpoint": "/health",
                "capabilities": [
                    "workflow_generation",
                    "workflow_validation",
                    "advanced_prompts",
                    "database_persistence"
                ]
            }
            
            response = await self.client.post(
                "/api/v1/services/register",
                json=payload
            )
            
            if response.status_code == 200:
                logger.info("AI service registered with API Gateway")
                return {"success": True, "data": response.json()}
            else:
                logger.warning(f"Service registration failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error registering service: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_workflow_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send workflow generation metrics to API Gateway
        
        Args:
            metrics: Metrics data to send
            
        Returns:
            Response from API Gateway
        """
        try:
            if not self.client:
                async with APIGatewayClient() as client:
                    return await client.send_workflow_metrics(metrics)
            
            response = await self.client.post(
                "/api/v1/metrics/ai-service",
                json=metrics
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                logger.warning(f"Metrics submission failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error sending metrics: {str(e)}")
            return {"success": False, "error": str(e)}


# Global API Gateway client instance
api_gateway_client = APIGatewayClient()
