"""
Database configuration for Flov7 platform.
Supabase client setup and database utilities.
"""

from supabase import create_client, Client
from shared.config.settings import settings
from typing import Optional


class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.service_supabase: Optional[Client] = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Supabase clients"""
        if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
            self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        
        if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
            self.service_supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    
    def get_client(self) -> Client:
        """Get Supabase client for authenticated requests"""
        if not self.supabase:
            raise ValueError("Supabase client not initialized. Check your environment variables.")
        return self.supabase
    
    def get_service_client(self) -> Client:
        """Get Supabase service client for admin operations"""
        if not self.service_supabase:
            raise ValueError("Supabase service client not initialized. Check your environment variables.")
        return self.service_supabase


# Global database manager instance
db_manager = DatabaseManager()
