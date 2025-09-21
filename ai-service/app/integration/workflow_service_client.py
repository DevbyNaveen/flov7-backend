"""
Workflow Service Client for AI Service Integration
Provides client functionality to send workflows from AI Service to Workflow Service for execution
"""

import httpx
import logging
from typing import Dict, Any, Optional
from app.config import config

logger = logging.getLogger(__name__)


class WorkflowServiceClient:
    """Client for communicating with Workflow Service"""
    
    def __init__(self):
        self.base_url = config.workflow_service_url
        self.timeout = config.workflow_service_timeout
        self.enabled = config.enable_workflow_execution
        
    async def execute_workflow(self, workflow_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Send a workflow to the Workflow Service for execution
        
        Args:
            workflow_data: The workflow definition to execute
            user_id: ID of the user requesting execution
            
        Returns:
            Execution response from Workflow Service
            
        Raises:
            Exception: If workflow execution fails
        """
        if not self.enabled:
            raise Exception("Workflow execution is disabled")
            
        endpoint = f"{self.base_url}/workflow/execute"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "workflow_data": workflow_data,
                    "user_id": user_id
                }
                
                logger.info(f"Sending workflow to execution service for user {user_id}")
                response = await client.post(endpoint, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Workflow execution started: {result.get('execution_id')}")
                    return result
                else:
                    error_msg = f"Workflow execution failed: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout while connecting to Workflow Service at {self.base_url}")
            raise Exception(f"Workflow Service timeout after {self.timeout}s")
        except httpx.ConnectError:
            logger.error(f"Failed to connect to Workflow Service at {self.base_url}")
            raise Exception("Workflow Service unavailable")
        except Exception as e:
            logger.error(f"Error executing workflow: {str(e)}")
            raise
    
    async def get_workflow_status(self, execution_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get the status of a workflow execution
        
        Args:
            execution_id: ID of the workflow execution
            user_id: ID of the user requesting status
            
        Returns:
            Status information from Workflow Service
        """
        if not self.enabled:
            raise Exception("Workflow execution is disabled")
            
        endpoint = f"{self.base_url}/workflow/status/{execution_id}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {"user_id": user_id}
                response = await client.get(endpoint, params=params)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    raise Exception("Workflow execution not found")
                else:
                    error_msg = f"Failed to get workflow status: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout while connecting to Workflow Service")
            raise Exception(f"Workflow Service timeout after {self.timeout}s")
        except httpx.ConnectError:
            logger.error(f"Failed to connect to Workflow Service")
            raise Exception("Workflow Service unavailable")
        except Exception as e:
            logger.error(f"Error getting workflow status: {str(e)}")
            raise
    
    async def get_execution_history(self, execution_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get execution history for a workflow
        
        Args:
            execution_id: ID of the workflow execution
            user_id: ID of the user requesting history
            
        Returns:
            Execution history from Workflow Service
        """
        if not self.enabled:
            raise Exception("Workflow execution is disabled")
            
        endpoint = f"{self.base_url}/workflow/history/{execution_id}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {"user_id": user_id}
                response = await client.get(endpoint, params=params)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    raise Exception("Workflow execution history not found")
                else:
                    error_msg = f"Failed to get execution history: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout while connecting to Workflow Service")
            raise Exception(f"Workflow Service timeout after {self.timeout}s")
        except httpx.ConnectError:
            logger.error(f"Failed to connect to Workflow Service")
            raise Exception("Workflow Service unavailable")
        except Exception as e:
            logger.error(f"Error getting execution history: {str(e)}")
            raise


# Global client instance
workflow_service_client = WorkflowServiceClient()
