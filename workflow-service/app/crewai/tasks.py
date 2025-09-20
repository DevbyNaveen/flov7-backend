"""
CrewAI tasks for Flov7 workflow service.
Defines tasks for multi-agent workflow processing.
"""

from crewai import Task
from typing import Optional, List
from app.crewai.agents import agent_manager
import logging

# Configure logging
logger = logging.getLogger(__name__)


class Flov7TaskManager:
    """Manager for CrewAI tasks in Flov7 workflows"""
    
    def __init__(self):
        self.tasks = {}
        self._initialize_tasks()
    
    def _initialize_tasks(self):
        """Initialize default tasks for workflow processing"""
        try:
            # Get agents
            coordinator = agent_manager.get_agent("workflow_coordinator")
            data_processor = agent_manager.get_agent("data_processor")
            action_executor = agent_manager.get_agent("action_executor")
            validator = agent_manager.get_agent("validator")
            
            if not all([coordinator, data_processor, action_executor, validator]):
                logger.warning("Some agents not available, tasks may not initialize properly")
                return
            
            # Define default tasks
            self.tasks = {
                "coordinate_workflow": self._create_coordinate_workflow_task(coordinator),
                "process_data": self._create_process_data_task(data_processor),
                "execute_actions": self._create_execute_actions_task(action_executor),
                "validate_results": self._create_validate_results_task(validator)
            }
            
            logger.info("CrewAI tasks initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize CrewAI tasks: {str(e)}")
    
    def _create_coordinate_workflow_task(self, agent) -> Task:
        """Create workflow coordination task"""
        return Task(
            description="Coordinate the execution of the workflow by assigning tasks to appropriate agents",
            agent=agent,
            expected_output="A plan for executing the workflow with task assignments"
        )
    
    def _create_process_data_task(self, agent) -> Task:
        """Create data processing task"""
        return Task(
            description="Process and transform data according to workflow requirements",
            agent=agent,
            expected_output="Processed data in the required format"
        )
    
    def _create_execute_actions_task(self, agent) -> Task:
        """Create action execution task"""
        return Task(
            description="Execute specific actions and tasks in the workflow",
            agent=agent,
            expected_output="Action execution results and status updates"
        )
    
    def _create_validate_results_task(self, agent) -> Task:
        """Create results validation task"""
        return Task(
            description="Validate workflow execution results and ensure quality",
            agent=agent,
            expected_output="Validation report with pass/fail status and any issues found"
        )
    
    def get_task(self, task_name: str) -> Optional[Task]:
        """
        Get a task by name
        
        Args:
            task_name: Name of the task to retrieve
            
        Returns:
            Task instance or None if not found
        """
        return self.tasks.get(task_name)
    
    def get_all_tasks(self) -> dict:
        """
        Get all tasks
        
        Returns:
            Dictionary of all task instances
        """
        return self.tasks
    
    def create_custom_task(self, description: str, agent_name: str, expected_output: str) -> Task:
        """
        Create a custom task for a specific agent
        
        Args:
            description: Task description
            agent_name: Name of the agent to assign the task to
            expected_output: Expected output of the task
            
        Returns:
            Custom Task instance
        """
        agent = agent_manager.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found")
        
        task = Task(
            description=description,
            agent=agent,
            expected_output=expected_output
        )
        
        # Store with a generated name
        task_name = f"custom_task_{len(self.tasks)}"
        self.tasks[task_name] = task
        
        return task


# Global task manager instance
task_manager = Flov7TaskManager()
