"""
CrewAI configuration for Flov7 workflow service.
Provides centralized configuration for CrewAI agents and multi-agent workflows.
"""

import os
from typing import Optional, Dict, Any
from datetime import timedelta

class CrewAIConfig:
    """Configuration class for CrewAI settings"""
    
    def __init__(self):
        # LLM Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "sk-placeholder")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
        
        # Agent Configuration
        self.max_iterations = int(os.getenv("CREWAI_MAX_ITERATIONS", "3"))
        self.max_rpm = int(os.getenv("CREWAI_MAX_RPM", "10"))
        self.agent_timeout = int(os.getenv("CREWAI_AGENT_TIMEOUT", "120"))
        self.allow_delegation = os.getenv("CREWAI_ALLOW_DELEGATION", "true").lower() == "true"
        
        # Workflow Configuration
        self.max_execution_time = int(os.getenv("CREWAI_MAX_EXECUTION_TIME", "300"))
        self.max_retries = int(os.getenv("CREWAI_MAX_RETRIES", "3"))
        self.retry_delay = int(os.getenv("CREWAI_RETRY_DELAY", "2"))
        
        # Memory Configuration
        self.enable_memory = os.getenv("CREWAI_ENABLE_MEMORY", "true").lower() == "true"
        self.memory_limit = int(os.getenv("CREWAI_MEMORY_LIMIT", "1000"))
        
        # Process Configuration
        self.default_process = os.getenv("CREWAI_DEFAULT_PROCESS", "sequential")
        self.verbose_mode = os.getenv("CREWAI_VERBOSE_MODE", "true").lower() == "true"
        
        # Feature Flags
        self.enable_crewai = os.getenv("ENABLE_CREWAI", "true").lower() == "true"
        self.enable_enhanced_agents = os.getenv("ENABLE_ENHANCED_AGENTS", "true").lower() == "true"
        
        # Rate Limiting
        self.rate_limit_requests = int(os.getenv("CREWAI_RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("CREWAI_RATE_LIMIT_WINDOW", "60"))
        
        # Error Handling
        self.error_handling_mode = os.getenv("CREWAI_ERROR_HANDLING", "graceful")
        self.fallback_enabled = os.getenv("CREWAI_FALLBACK_ENABLED", "true").lower() == "true"
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate CrewAI configuration"""
        issues = []
        warnings = []
        
        if not self.openai_api_key or self.openai_api_key == "sk-placeholder":
            warnings.append("OPENAI_API_KEY not set - using mock responses")
        
        if self.max_execution_time < 60:
            issues.append("CREWAI_MAX_EXECUTION_TIME too low (minimum 60 seconds)")
        
        if self.max_retries < 1 or self.max_retries > 5:
            issues.append("CREWAI_MAX_RETRIES should be between 1 and 5")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        return {
            "api_key": self.openai_api_key,
            "model": self.openai_model,
            "temperature": self.openai_temperature,
            "max_tokens": self.openai_max_tokens
        }
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration"""
        return {
            "max_iterations": self.max_iterations,
            "max_rpm": self.max_rpm,
            "timeout": self.agent_timeout,
            "allow_delegation": self.allow_delegation
        }
    
    def get_workflow_config(self) -> Dict[str, Any]:
        """Get workflow configuration"""
        return {
            "max_execution_time": self.max_execution_time,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "enable_memory": self.enable_memory,
            "memory_limit": self.memory_limit,
            "verbose_mode": self.verbose_mode
        }

# Global configuration instance
crewai_config = CrewAIConfig()
