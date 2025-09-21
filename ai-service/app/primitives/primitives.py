"""
Primitive definitions for Flov7 AI service.
Implementation of the 5-primitives system for workflow generation.
"""

from typing import Dict, Any, Optional, List
import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared.constants.primitives import PRIMITIVES
from shared.models.primitive import PrimitiveTypes, PrimitiveCategories

# Configure logging
logger = logging.getLogger(__name__)


class PrimitiveManager:
    """Manager for the 5-primitives system"""
    
    def __init__(self):
        self.primitives = PRIMITIVES
        self._load_custom_primitives()
    
    def _load_custom_primitives(self):
        """Load custom primitives from database or configuration"""
        # In a real implementation, this would load primitives from the database
        # For now, we'll use the default primitives
        pass
    
    def get_primitive(self, primitive_type: str) -> Optional[Dict[str, Any]]:
        """Get a primitive definition by type"""
        return self.primitives.get(primitive_type)
    
    def get_all_primitives(self) -> Dict[str, Any]:
        """Get all primitive definitions"""
        return self.primitives
    
    def get_primitive_types(self) -> List[str]:
        """Get all primitive types"""
        return list(self.primitives.keys())
    
    def validate_primitive_type(self, primitive_type: str) -> bool:
        """Validate if a primitive type exists"""
        return primitive_type in self.primitives
    
    def get_primitive_display_name(self, primitive_type: str) -> str:
        """Get the display name of a primitive"""
        primitive = self.primitives.get(primitive_type)
        if primitive:
            return primitive["display_name"]
        return primitive_type.title()
    
    def get_primitive_description(self, primitive_type: str) -> str:
        """Get the description of a primitive"""
        primitive = self.primitives.get(primitive_type)
        if primitive:
            return primitive["description"]
        return ""
    
    def get_primitive_icon(self, primitive_type: str) -> str:
        """Get the icon of a primitive"""
        primitive = self.primitives.get(primitive_type)
        if primitive:
            return primitive["icon"]
        return "help"
    
    def get_primitive_color(self, primitive_type: str) -> str:
        """Get the color of a primitive"""
        primitive = self.primitives.get(primitive_type)
        if primitive:
            return primitive["color"]
        return "#9E9E9E"


# Global primitive manager instance
primitive_manager = PrimitiveManager()
