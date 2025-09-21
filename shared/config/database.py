"""
Database configuration for Flov7 platform.
Supabase client setup and database utilities.
"""

from supabase import create_client, Client
from shared.config.settings import settings
from typing import Optional, Dict, Any
import logging
import time
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection manager with retry logic and error handling"""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.service_supabase: Optional[Client] = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Supabase clients with error handling"""
        try:
            if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
                self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
                logger.info("✅ Regular Supabase client initialized")
            else:
                logger.warning("❌ Missing Supabase credentials for regular client")
            
            if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
                self.service_supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
                logger.info("✅ Service Supabase client initialized")
            else:
                logger.warning("❌ Missing Supabase credentials for service client")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase clients: {e}")
            raise
    
    def get_client(self) -> Client:
        """Get Supabase client for authenticated requests with retry logic"""
        if not self.supabase:
            raise ValueError("Supabase client not initialized. Check your environment variables.")
        return self.supabase
    
    def get_service_client(self) -> Client:
        """Get Supabase service client for admin operations with retry logic"""
        if not self.service_supabase:
            raise ValueError("Supabase service client not initialized. Check your environment variables.")
        return self.service_supabase
    
    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            # Simple query to test connection
            client = self.get_client()
            result = client.table("users").select("count", count="exact").limit(1).execute()
            logger.info("✅ Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for database connections"""
        health_status = {
            "database_connection": False,
            "tables_exist": False,
            "regular_client": False,
            "service_client": False,
            "error": None
        }
        
        try:
            # Test regular client
            if self.supabase:
                try:
                    self.supabase.table("users").select("count", count="exact").limit(1).execute()
                    health_status["regular_client"] = True
                except Exception as e:
                    health_status["error"] = str(e)
            
            # Test service client
            if self.service_supabase:
                try:
                    self.service_supabase.table("users").select("count", count="exact").limit(1).execute()
                    health_status["service_client"] = True
                except Exception as e:
                    health_status["error"] = str(e)
            
            # Test table existence
            expected_tables = [
                'users', 'workflows', 'workflow_executions', 'primitives',
                'user_integrations', 'workflow_templates', 'audit_logs',
                'api_keys', 'notifications', 'deployments'
            ]
            
            missing_tables = []
            if self.service_supabase:
                for table in expected_tables:
                    try:
                        self.service_supabase.table(table).select("count", count="exact").limit(1).execute()
                    except Exception:
                        missing_tables.append(table)
                
                health_status["tables_exist"] = len(missing_tables) == 0
                if missing_tables:
                    health_status["missing_tables"] = missing_tables
            
            health_status["database_connection"] = health_status["regular_client"] or health_status["service_client"]
            
        except Exception as e:
            health_status["error"] = str(e)
        
        return health_status


# Global database manager instance
db_manager = DatabaseManager()
