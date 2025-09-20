"""
CrewAI agents for Flov7 workflow service.
Defines AI agents for multi-agent workflow processing.
"""

from crewai import Agent
from typing import Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)


class Flov7AgentManager:
    """Manager for CrewAI agents in Flov7 workflows"""
    
    def __init__(self):
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize default agents for workflow processing"""
        try:
            # Define default agents
            self.agents = {
                "workflow_coordinator": self._create_workflow_coordinator(),
                "data_processor": self._create_data_processor(),
                "action_executor": self._create_action_executor(),
                "validator": self._create_validator()
            }
            
            logger.info("CrewAI agents initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize CrewAI agents: {str(e)}")
    
    def _create_workflow_coordinator(self) -> Agent:
        """Create workflow coordinator agent"""
        return Agent(
            role="Workflow Coordinator",
            goal="Coordinate and orchestrate workflow execution across multiple agents",
            backstory="You are an expert workflow coordinator that manages complex multi-step processes",
            verbose=True,
            allow_delegation=True
        )
    
    def _create_data_processor(self) -> Agent:
        """Create data processor agent"""
        return Agent(
            role="Data Processor",
            goal="Process and transform data according to workflow requirements",
            backstory="You are a skilled data processor that handles various data formats and transformations",
            verbose=True,
            allow_delegation=False
        )
    
    def _create_action_executor(self) -> Agent:
        """Create action executor agent"""
        return Agent(
            role="Action Executor",
            goal="Execute specific actions and tasks in the workflow",
            backstory="You are an action executor that performs tasks like API calls, file operations, etc.",
            verbose=True,
            allow_delegation=False
        )
    
    def _create_validator(self) -> Agent:
        """Create validator agent"""
        return Agent(
            role="Workflow Validator",
            goal="Validate workflow execution results and ensure quality",
            backstory="You are a meticulous validator that checks workflow outputs for correctness",
            verbose=True,
            allow_delegation=False
        )
    
    def get_agent(self, agent_name: str) -> Optional[Agent]:
        """
        Get an agent by name
        
        Args:
            agent_name: Name of the agent to retrieve
            
        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_name)
    
    def get_all_agents(self) -> dict:
        """
        Get all agents
        
        Returns:
            Dictionary of all agent instances
        """
        return self.agents


# Global agent manager instance
agent_manager = Flov7AgentManager()
