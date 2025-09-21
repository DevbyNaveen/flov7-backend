"""
Temporal worker implementation for Flov7 workflow service.
Handles workflow and activity registration and execution.
"""

import asyncio
import logging
from temporalio.worker import Worker
from temporalio.client import Client
from typing import List
import signal
import sys

# Import workflows and activities
from app.temporal.workflows import WorkflowExecution, WorkflowValidation
from app.temporal.activities import workflow_activities
from app.temporal.client import temporal_client_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TemporalWorkerManager:
    """Manages Temporal worker lifecycle and configuration"""
    
    def __init__(self):
        self.worker: Worker = None
        self.shutdown_event = asyncio.Event()
        self.task_queue_name = "flov7-workflow-task-queue"
    
    async def start_worker(self) -> None:
        """
        Start the Temporal worker with proper configuration
        """
        try:
            # Initialize Temporal client
            client = await temporal_client_manager.get_client_async()
            if not client:
                raise RuntimeError("Failed to connect to Temporal server")
            
            logger.info(f"Starting Temporal worker for task queue: {self.task_queue_name}")
            
            # Create worker with workflows and activities
            self.worker = Worker(
                client,
                task_queue=self.task_queue_name,
                workflows=[
                    WorkflowExecution,
                    WorkflowValidation
                ],
                activities=[
                    workflow_activities.execute_node,
                    workflow_activities.validate_workflow_structure,
                    workflow_activities.update_execution_status,
                    workflow_activities.log_workflow_event
                ],
                max_concurrent_workflow_tasks=10,
                max_concurrent_activities=5,
                max_activities_per_second=10,
                max_task_queue_activities_per_second=20
            )
            
            logger.info("Temporal worker started successfully")
            
            # Setup graceful shutdown
            self._setup_signal_handlers()
            
            # Run worker until shutdown
            await self.worker.run()
            
        except Exception as e:
            logger.error(f"Failed to start Temporal worker: {str(e)}")
            raise
    
    async def shutdown_worker(self) -> None:
        """
        Gracefully shutdown the Temporal worker
        """
        try:
            logger.info("Shutting down Temporal worker...")
            
            if self.worker:
                await self.worker.shutdown()
                logger.info("Temporal worker shutdown completed")
            
            # Close Temporal client
            await temporal_client_manager.close()
            
        except Exception as e:
            logger.error(f"Error during worker shutdown: {str(e)}")
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


async def run_worker() -> None:
    """
    Main function to run the Temporal worker
    """
    worker_manager = TemporalWorkerManager()
    
    try:
        await worker_manager.start_worker()
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
    except Exception as e:
        logger.error(f"Worker error: {str(e)}")
        sys.exit(1)
    finally:
        await worker_manager.shutdown_worker()


async def start_worker_async() -> TemporalWorkerManager:
    """
    Start worker asynchronously and return manager
    
    Returns:
        TemporalWorkerManager instance
    """
    worker_manager = TemporalWorkerManager()
    
    # Start worker in background
    asyncio.create_task(worker_manager.start_worker())
    
    return worker_manager


if __name__ == "__main__":
    """Entry point for running the worker directly"""
    logger.info("Starting Flov7 Temporal worker...")
    asyncio.run(run_worker())
