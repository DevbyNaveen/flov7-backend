"""
Temporal configuration for Flov7 workflow service.
Provides centralized configuration for Temporal client and worker settings.
"""

import os
from typing import Optional
from datetime import timedelta
from temporalio.common import RetryPolicy


class TemporalConfig:
    """Configuration class for Temporal settings"""
    
    def __init__(self):
        # Server connection settings
        self.temporal_host = os.getenv("TEMPORAL_HOST", "localhost:7233")
        self.temporal_namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
        self.connection_timeout = int(os.getenv("TEMPORAL_CONNECTION_TIMEOUT", "10"))
        
        # Worker settings
        self.task_queue_name = os.getenv("TEMPORAL_TASK_QUEUE", "flov7-workflow-task-queue")
        self.max_concurrent_workflow_tasks = int(os.getenv("TEMPORAL_MAX_CONCURRENT_WORKFLOWS", "10"))
        self.max_concurrent_activities = int(os.getenv("TEMPORAL_MAX_CONCURRENT_ACTIVITIES", "5"))
        self.max_activities_per_second = int(os.getenv("TEMPORAL_MAX_ACTIVITIES_PER_SECOND", "10"))
        self.max_task_queue_activities_per_second = int(os.getenv("TEMPORAL_MAX_TASK_QUEUE_ACTIVITIES_PER_SECOND", "20"))
        
        # Workflow settings
        self.workflow_execution_timeout = timedelta(minutes=int(os.getenv("TEMPORAL_WORKFLOW_TIMEOUT_MINUTES", "30")))
        self.workflow_run_timeout = timedelta(minutes=int(os.getenv("TEMPORAL_WORKFLOW_RUN_TIMEOUT_MINUTES", "30")))
        
        # Activity settings
        self.activity_start_to_close_timeout = timedelta(minutes=int(os.getenv("TEMPORAL_ACTIVITY_TIMEOUT_MINUTES", "5")))
        self.activity_schedule_to_close_timeout = timedelta(minutes=int(os.getenv("TEMPORAL_ACTIVITY_SCHEDULE_TIMEOUT_MINUTES", "10")))
        
        # Retry policies
        self.workflow_retry_policy = RetryPolicy(
            maximum_attempts=int(os.getenv("TEMPORAL_WORKFLOW_MAX_RETRIES", "3")),
            initial_interval=timedelta(seconds=int(os.getenv("TEMPORAL_WORKFLOW_INITIAL_INTERVAL_SECONDS", "1"))),
            maximum_interval=timedelta(seconds=int(os.getenv("TEMPORAL_WORKFLOW_MAX_INTERVAL_SECONDS", "10"))),
            backoff_coefficient=float(os.getenv("TEMPORAL_WORKFLOW_BACKOFF_COEFFICIENT", "2.0"))
        )
        
        self.activity_retry_policy = RetryPolicy(
            maximum_attempts=int(os.getenv("TEMPORAL_ACTIVITY_MAX_RETRIES", "3")),
            initial_interval=timedelta(seconds=int(os.getenv("TEMPORAL_ACTIVITY_INITIAL_INTERVAL_SECONDS", "1"))),
            maximum_interval=timedelta(seconds=int(os.getenv("TEMPORAL_ACTIVITY_MAX_INTERVAL_SECONDS", "10"))),
            backoff_coefficient=float(os.getenv("TEMPORAL_ACTIVITY_BACKOFF_COEFFICIENT", "2.0"))
        )
        
        # Node-specific settings
        self.node_execution_timeout = timedelta(minutes=int(os.getenv("TEMPORAL_NODE_TIMEOUT_MINUTES", "5")))
        self.validation_timeout = timedelta(seconds=int(os.getenv("TEMPORAL_VALIDATION_TIMEOUT_SECONDS", "30")))
        
        # Feature flags
        self.start_worker_on_startup = os.getenv("START_TEMPORAL_WORKER", "false").lower() == "true"
        self.enable_temporal_features = os.getenv("ENABLE_TEMPORAL_FEATURES", "true").lower() == "true"
        
        # Monitoring and observability
        self.enable_worker_metrics = os.getenv("TEMPORAL_ENABLE_WORKER_METRICS", "false").lower() == "true"
        self.worker_metrics_port = int(os.getenv("TEMPORAL_WORKER_METRICS_PORT", "9090"))
        
        # Health check settings
        self.health_check_interval = int(os.getenv("TEMPORAL_HEALTH_CHECK_INTERVAL_SECONDS", "30"))
        self.max_connection_retries = int(os.getenv("TEMPORAL_MAX_CONNECTION_RETRIES", "5"))
    
    def validate_config(self) -> bool:
        """
        Validate Temporal configuration
        
        Returns:
            True if configuration is valid, False otherwise
        """
        if not self.temporal_host:
            print("ERROR: TEMPORAL_HOST is not configured")
            return False
        
        if not self.temporal_namespace:
            print("ERROR: TEMPORAL_NAMESPACE is not configured")
            return False
        
        if self.max_concurrent_workflow_tasks <= 0:
            print("ERROR: TEMPORAL_MAX_CONCURRENT_WORKFLOWS must be positive")
            return False
        
        if self.max_concurrent_activities <= 0:
            print("ERROR: TEMPORAL_MAX_CONCURRENT_ACTIVITIES must be positive")
            return False
        
        return True
    
    def get_worker_config(self) -> dict:
        """
        Get worker configuration as dictionary
        
        Returns:
            Worker configuration dictionary
        """
        return {
            "task_queue": self.task_queue_name,
            "max_concurrent_workflow_tasks": self.max_concurrent_workflow_tasks,
            "max_concurrent_activities": self.max_concurrent_activities,
            "max_activities_per_second": self.max_activities_per_second,
            "max_task_queue_activities_per_second": self.max_task_queue_activities_per_second
        }
    
    def get_client_config(self) -> dict:
        """
        Get client configuration as dictionary
        
        Returns:
            Client configuration dictionary
        """
        return {
            "target_host": self.temporal_host,
            "namespace": self.temporal_namespace,
            "rpc_timeout": timedelta(seconds=self.connection_timeout)
        }


# Global configuration instance
temporal_config = TemporalConfig()
