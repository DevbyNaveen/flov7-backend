#!/usr/bin/env python3
"""
Temporal worker entry point for Flov7 workflow service.
This script can be run independently to start the Temporal worker.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the Temporal worker"""
    try:
        from app.temporal.worker import run_worker
        
        logger.info("Starting Flov7 Temporal worker...")
        logger.info("Worker configuration:")
        logger.info("  Task Queue: flov7-workflow-task-queue")
        logger.info("  Workflows: WorkflowExecution, WorkflowValidation")
        logger.info("  Activities: execute_node, validate_workflow_structure, update_execution_status, log_workflow_event")
        
        await run_worker()
        
    except ImportError as e:
        logger.error(f"Failed to import worker module: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Worker failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
