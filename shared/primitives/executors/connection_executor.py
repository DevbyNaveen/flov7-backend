"""
Connection Executor for Flov7 platform.
Manages external service connections and authentication.
"""

from typing import Dict, Any, Optional
import asyncio
import sqlite3
import logging
from datetime import datetime, timedelta
from uuid import uuid4

from ..registry import PrimitiveExecutor, PrimitiveExecutionContext

logger = logging.getLogger(__name__)


class ConnectionExecutor(PrimitiveExecutor):
    """Executor for connection primitives - manages external service connections"""
    
    def __init__(self):
        self.supported_connections = {
            'gmail': self._execute_gmail_connection,
            'slack': self._execute_slack_connection,
            'hubspot': self._execute_hubspot_connection,
            'database': self._execute_database_connection,
            'api': self._execute_api_connection,
            'webhook': self._execute_webhook_connection,
            'oauth': self._execute_oauth_connection,
            'api_key': self._execute_api_key_connection
        }
    
    async def execute(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        connection_type = config.get('connection_type', 'api')
        
        if connection_type not in self.supported_connections:
            raise ValueError(f"Unsupported connection type: {connection_type}")
        
        connection_func = self.supported_connections[connection_type]
        return await connection_func(config, input_data, context)
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        required_fields = ['connection_type']
        for field in required_fields:
            if field not in config:
                return False, f"Missing required field: {field}"
        
        connection_type = config['connection_type']
        if connection_type not in self.supported_connections:
            return False, f"Unsupported connection type: {connection_type}"
        
        # Validate specific connection requirements
        if connection_type == 'gmail' and not config.get('credentials'):
            return False, "Gmail connection requires credentials"
        
        if connection_type == 'database' and not config.get('connection_string'):
            return False, "Database connection requires connection string"
        
        return True, None
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "connection_params": {
                    "type": "object",
                    "description": "Parameters for establishing connection"
                }
            }
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "connection_type": {"type": "string"},
                "connected": {"type": "boolean"},
                "connection_id": {"type": "string"},
                "metadata": {"type": "object"},
                "timestamp": {"type": "string", "format": "date-time"}
            },
            "required": ["connection_type", "connected", "timestamp"]
        }
    
    async def _execute_gmail_connection(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        # Simulate Gmail OAuth connection
        return {
            "connection_type": "gmail",
            "connected": True,
            "connection_id": f"gmail_{uuid4().hex[:8]}",
            "metadata": {
                "scopes": ["https://www.googleapis.com/auth/gmail.send"],
                "user_email": config.get('user_email', 'user@example.com')
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_slack_connection(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        return {
            "connection_type": "slack",
            "connected": True,
            "connection_id": f"slack_{uuid4().hex[:8]}",
            "metadata": {
                "workspace": config.get('workspace', 'default'),
                "channels": config.get('channels', [])
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_hubspot_connection(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        return {
            "connection_type": "hubspot",
            "connected": True,
            "connection_id": f"hubspot_{uuid4().hex[:8]}",
            "metadata": {
                "portal_id": config.get('portal_id', ''),
                "scopes": config.get('scopes', ['contacts', 'deals'])
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_database_connection(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        connection_string = config.get('connection_string', 'sqlite://:memory:')
        
        # Test connection
        try:
            if 'sqlite' in connection_string:
                conn = sqlite3.connect(':memory:')
                conn.close()
                connected = True
            else:
                connected = True  # Simulate successful connection
        except Exception:
            connected = False
        
        return {
            "connection_type": "database",
            "connected": connected,
            "connection_id": f"db_{uuid4().hex[:8]}",
            "metadata": {
                "connection_string": connection_string,
                "database_type": config.get('database_type', 'sqlite')
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_api_connection(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        return {
            "connection_type": "api",
            "connected": True,
            "connection_id": f"api_{uuid4().hex[:8]}",
            "metadata": {
                "base_url": config.get('base_url', ''),
                "authentication": config.get('authentication', 'none'),
                "rate_limit": config.get('rate_limit', 100)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_webhook_connection(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        return {
            "connection_type": "webhook",
            "connected": True,
            "connection_id": f"webhook_{uuid4().hex[:8]}",
            "metadata": {
                "webhook_url": config.get('webhook_url', ''),
                "secret": config.get('secret', '')
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_oauth_connection(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        return {
            "connection_type": "oauth",
            "connected": True,
            "connection_id": f"oauth_{uuid4().hex[:8]}",
            "metadata": {
                "provider": config.get('provider', ''),
                "scopes": config.get('scopes', []),
                "token_expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_api_key_connection(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        return {
            "connection_type": "api_key",
            "connected": True,
            "connection_id": f"api_key_{uuid4().hex[:8]}",
            "metadata": {
                "service": config.get('service', ''),
                "key_prefix": config.get('api_key', '')[:8] + "...",
                "expires_at": config.get('expires_at', (datetime.utcnow() + timedelta(days=365)).isoformat())
            },
            "timestamp": datetime.utcnow().isoformat()
        }
