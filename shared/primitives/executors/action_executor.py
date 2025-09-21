"""
Action Executor for Flov7 platform.
Performs specific tasks and operations.
"""

from typing import Dict, Any, Optional
import asyncio
import aiohttp
import logging
from datetime import datetime
from uuid import uuid4

from ..registry import PrimitiveExecutor, PrimitiveExecutionContext

logger = logging.getLogger(__name__)


class ActionExecutor(PrimitiveExecutor):
    """Executor for action primitives - performs specific tasks"""
    
    def __init__(self):
        self.supported_actions = {
            'ai_process': self._execute_ai_process,
            'api_call': self._execute_api_call,
            'email_send': self._execute_email_send,
            'db_query': self._execute_db_query,
            'notification': self._execute_notification,
            'transform': self._execute_transform,
            'wait': self._execute_wait,
            'custom': self._execute_custom
        }
    
    async def execute(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        action_type = config.get('action_type', 'custom')
        
        if action_type not in self.supported_actions:
            raise ValueError(f"Unsupported action type: {action_type}")
        
        action_func = self.supported_actions[action_type]
        return await action_func(config, input_data, context)
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        required_fields = ['action_type']
        for field in required_fields:
            if field not in config:
                return False, f"Missing required field: {field}"
        
        action_type = config['action_type']
        if action_type not in self.supported_actions:
            return False, f"Unsupported action type: {action_type}"
        
        return True, None
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Input data for the action"
                }
            }
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action_type": {"type": "string"},
                "result": {"type": "object"},
                "success": {"type": "boolean"},
                "execution_time": {"type": "number"},
                "timestamp": {"type": "string", "format": "date-time"}
            },
            "required": ["action_type", "success", "timestamp"]
        }
    
    async def _execute_ai_process(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        # Simulate AI processing
        await asyncio.sleep(0.1)  # Simulate processing time
        
        prompt = config.get('prompt', 'Process the input data')
        model = config.get('model', 'gpt-3.5-turbo')
        
        return {
            "action_type": "ai_process",
            "result": {
                "processed_data": f"AI processed: {input_data.get('data', {})}",
                "model_used": model,
                "prompt": prompt
            },
            "success": True,
            "execution_time": context.get_execution_time(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_api_call(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        url = config.get('url', '')
        method = config.get('method', 'GET')
        headers = config.get('headers', {})
        body = config.get('body', input_data.get('data', {}))
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, json=body, headers=headers) as response:
                    content_type = response.headers.get('content-type', '')
                    
                    if 'application/json' in content_type:
                        body_data = await response.json()
                    else:
                        body_data = await response.text()
                    
                    result = {
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "body": body_data
                    }
                    
                    return {
                        "action_type": "api_call",
                        "result": result,
                        "success": response.status < 400,
                        "execution_time": context.get_execution_time(),
                        "timestamp": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            return {
                "action_type": "api_call",
                "result": {"error": str(e)},
                "success": False,
                "execution_time": context.get_execution_time(),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _execute_email_send(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        to_email = config.get('to_email', '')
        subject = config.get('subject', 'Flov7 Workflow Notification')
        body = config.get('body', str(input_data.get('data', {})))
        
        # Simulate email sending
        await asyncio.sleep(0.1)
        
        return {
            "action_type": "email_send",
            "result": {
                "to": to_email,
                "subject": subject,
                "body_length": len(body),
                "message_id": f"msg_{uuid4().hex[:8]}"
            },
            "success": True,
            "execution_time": context.get_execution_time(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_db_query(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        query = config.get('query', '')
        params = config.get('params', input_data.get('data', {}))
        
        # Simulate database query
        await asyncio.sleep(0.1)
        
        return {
            "action_type": "db_query",
            "result": {
                "query": query,
                "params": params,
                "rows_affected": 1,
                "data": [{"id": 1, "result": "query_result"}]
            },
            "success": True,
            "execution_time": context.get_execution_time(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_notification(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        channel = config.get('channel', 'slack')
        message = config.get('message', str(input_data.get('data', {})))
        
        # Simulate notification
        await asyncio.sleep(0.1)
        
        return {
            "action_type": "notification",
            "result": {
                "channel": channel,
                "message": message,
                "notification_id": f"notif_{uuid4().hex[:8]}"
            },
            "success": True,
            "execution_time": context.get_execution_time(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_transform(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        transform_type = config.get('transform_type', 'json')
        
        # Simulate data transformation
        await asyncio.sleep(0.1)
        
        original_data = input_data.get('data', {})
        transformed_data = {
            "transformed": True,
            "original": original_data,
            "transform_type": transform_type
        }
        
        return {
            "action_type": "transform",
            "result": transformed_data,
            "success": True,
            "execution_time": context.get_execution_time(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_wait(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        duration = config.get('duration', 1)
        unit = config.get('unit', 'seconds')
        
        # Convert to seconds
        if unit == 'minutes':
            duration *= 60
        elif unit == 'hours':
            duration *= 3600
        
        await asyncio.sleep(duration)
        
        return {
            "action_type": "wait",
            "result": {
                "waited_for": f"{duration} {unit}",
                "actual_seconds": duration if unit == 'seconds' else duration * (60 if unit == 'minutes' else 3600)
            },
            "success": True,
            "execution_time": context.get_execution_time(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_custom(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        custom_code = config.get('code', '')
        
        # Simulate custom code execution
        await asyncio.sleep(0.1)
        
        return {
            "action_type": "custom",
            "result": {
                "custom_result": f"Executed custom code: {custom_code[:50]}...",
                "input_received": input_data.get('data', {})
            },
            "success": True,
            "execution_time": context.get_execution_time(),
            "timestamp": datetime.utcnow().isoformat()
        }
