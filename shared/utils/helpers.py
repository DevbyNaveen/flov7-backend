"""
Helper utilities for Flov7 platform.
Common utility functions used across services.
"""

import hashlib
import secrets
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    """Hash a token for secure storage"""
    return hashlib.sha256(token.encode()).hexdigest()


def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> bool:
    """Validate password strength"""
    # At least 8 characters, one uppercase, one lowercase, one digit
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    return has_upper and has_lower and has_digit


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string"""
    return dt.isoformat() if dt else None


def uuid_to_str(uuid_obj: UUID) -> str:
    """Convert UUID to string"""
    return str(uuid_obj) if uuid_obj else None


def deep_merge_dicts(dict1: Dict[Any, Any], dict2: Dict[Any, Any]) -> Dict[Any, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def camel_to_snake(camel_str: str) -> str:
    """Convert camelCase to snake_case"""
    import re
    snake_str = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', snake_str).lower()


def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate string to max_length and add ellipsis if needed"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def is_valid_json(json_str: str) -> bool:
    """Check if string is valid JSON"""
    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Get nested dictionary value using dot notation path"""
    keys = path.split('.')
    current = data
    
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def set_nested_value(data: Dict[str, Any], path: str, value: Any) -> None:
    """Set nested dictionary value using dot notation path"""
    keys = path.split('.')
    current = data
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
