"""
Trigger Executor for Flov7 platform.
Handles workflow initiation based on various trigger types.
"""

from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
import logging
from uuid import uuid4

from ..registry import PrimitiveExecutor, PrimitiveExecutionContext

logger = logging.getLogger(__name__)


class TriggerExecutor(PrimitiveExecutor):
    """Executor for trigger primitives - handles workflow initiation"""
    
    def __init__(self):
        self.supported_triggers = {
            'webhook': self._execute_webhook_trigger,
            'schedule': self._execute_schedule_trigger,
            'database': self._execute_database_trigger,
            'manual': self._execute_manual_trigger,
            'api': self._execute_api_trigger,
            'email': self._execute_email_trigger,
            'sms': self._execute_sms_trigger,
            'iot': self._execute_iot_trigger
        }
    
    async def execute(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        trigger_type = config.get('trigger_type', 'manual')
        
        if trigger_type not in self.supported_triggers:
            raise ValueError(f"Unsupported trigger type: {trigger_type}")
        
        trigger_func = self.supported_triggers[trigger_type]
        return await trigger_func(config, input_data, context)
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        required_fields = ['trigger_type']
        for field in required_fields:
            if field not in config:
                return False, f"Missing required field: {field}"
        
        trigger_type = config['trigger_type']
        if trigger_type not in self.supported_triggers:
            return False, f"Unsupported trigger type: {trigger_type}"
        
        return True, None
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "trigger_data": {
                    "type": "object",
                    "description": "Data that triggered this workflow"
                }
            }
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "triggered": {"type": "boolean"},
                "trigger_type": {"type": "string"},
                "trigger_data": {"type": "object"},
                "timestamp": {"type": "string", "format": "date-time"}
            },
            "required": ["triggered", "trigger_type", "timestamp"]
        }
    
    async def _execute_webhook_trigger(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        return {
            "triggered": True,
            "trigger_type": "webhook",
            "trigger_data": input_data.get('trigger_data', {}),
            "timestamp": datetime.utcnow().isoformat(),
            "webhook_url": config.get('webhook_url', '/webhook'),
            "method": config.get('method', 'POST')
        }
    
    async def _execute_schedule_trigger(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        return {
            "triggered": True,
            "trigger_type": "schedule",
            "trigger_data": input_data.get('trigger_data', {}),
            "timestamp": datetime.utcnow().isoformat(),
            "schedule": config.get('schedule', '0 0 * * *'),
            "timezone": config.get('timezone', 'UTC')
        }
    
    async def _execute_database_trigger(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        return {
            "triggered": True,
            "trigger_type": "database",
            "trigger_data": input_data.get('trigger_data', {}),
            "timestamp": datetime.utcnow().isoformat(),
            "table": config.get('table', ''),
            "operation": config.get('operation', 'INSERT')
        }
    
    async def _execute_manual_trigger(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        return {
            "triggered": True,
            "trigger_type": "manual",
            "trigger_data": input_data.get('trigger_data', {}),
            "timestamp": datetime.utcnow().isoformat(),
            "initiated_by": context.user_id
        }
    
    async def _execute_api_trigger(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        return {
            "triggered": True,
            "trigger_type": "api",
            "trigger_data": input_data.get('trigger_data', {}),
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": config.get('endpoint', '/api/trigger')
        }
    
    async def _execute_email_trigger(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        return {
            "triggered": True,
            "trigger_type": "email",
            "trigger_data": input_data.get('trigger_data', {}),
            "timestamp": datetime.utcnow().isoformat(),
            "from": config.get('from_email', ''),
            "subject": config.get('subject_contains', '')
        }
    
    async def _execute_sms_trigger(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        return {
            "triggered": True,
            "trigger_type": "sms",
            "trigger_data": input_data.get('trigger_data', {}),
            "timestamp": datetime.utcnow().isoformat(),
            "from_number": config.get('from_number', ''),
            "message_contains": config.get('message_contains', '')
        }
    
    async def _execute_iot_trigger(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        return {
            "triggered": True,
            "trigger_type": "iot",
            "trigger_data": input_data.get('trigger_data', {}),
            "timestamp": datetime.utcnow().isoformat(),
            "device_id": config.get('device_id', ''),
            "event_type": config.get('event_type', '')
        }
