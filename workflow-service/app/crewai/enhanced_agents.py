"""
Enhanced CrewAI agents for Flov7 workflow service with specific roles and capabilities.
Provides comprehensive multi-agent system for workflow processing.
"""

from crewai import Agent
from langchain_core.language_models.fake import FakeListLLM
from langchain_openai import ChatOpenAI
from typing import Optional, Dict, Any, List
import logging
import os

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedAgentManager:
    """Enhanced manager for CrewAI agents with specific workflow capabilities"""
    
    def __init__(self):
        self.agents = {}
        self.llm = self._setup_llm()
        self._initialize_enhanced_agents()
    
    def _setup_llm(self):
        """Setup LLM configuration for agents"""
        try:
            # Use OpenAI by default, fallback to local if needed
            api_key = os.getenv("OPENAI_API_KEY", "sk-placeholder")
            if api_key == "sk-placeholder" or not api_key:
                logger.warning("Using mock LLM for testing (no real API key provided)")
                return FakeListLLM(responses=["Mock response for testing CrewAI integration."])
            
            return ChatOpenAI(
                openai_api_key=api_key,
                model_name=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                temperature=0.7
            )
        except Exception as e:
            logger.warning(f"Failed to setup LLM: {e}, using mock LLM")
            return FakeListLLM(responses=["Mock response for testing CrewAI integration."])

        except Exception as e:

            return None
    
    def _initialize_enhanced_agents(self):
        """Initialize enhanced agents with specific roles"""
        try:
            self.agents = {
                "workflow_orchestrator": self._create_workflow_orchestrator(),
                "data_analyst": self._create_data_analyst(),
                "api_specialist": self._create_api_specialist(),
                "validation_expert": self._create_validation_expert(),
                "error_handler": self._create_error_handler(),
                "report_generator": self._create_report_generator()
            }
            logger.info("Enhanced CrewAI agents initialized successfully")


        except Exception as e:
            logger.error(f"Failed to initialize enhanced agents: {str(e)}")
    
    def _create_workflow_orchestrator(self) -> Agent:
        """Create workflow orchestrator agent"""
        return Agent(
            role="Workflow Orchestrator",
            goal="Design and coordinate complex multi-agent workflows with optimal resource allocation",
            backstory="""You are an expert workflow orchestrator with deep understanding of business processes, 
            system integrations, and multi-agent coordination. You excel at breaking down complex workflows 
            into manageable tasks and ensuring seamless execution across distributed systems.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=True,
            max_iter=3,
            max_rpm=10
        )
    
    def _create_data_analyst(self) -> Agent:
        """Create data analyst agent"""
        return Agent(
            role="Data Analyst",
            goal="Process, analyze, and transform data according to workflow requirements",
            backstory="""You are a skilled data analyst with expertise in data transformation, validation, 
            and analysis. You can handle various data formats, perform complex calculations, and provide 
            actionable insights from raw data.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=2,
            max_rpm=15
        )
    
    def _create_api_specialist(self) -> Agent:
        """Create API specialist agent"""
        return Agent(
            role="API Integration Specialist",
            goal="Execute API calls, handle responses, and manage external service integrations",
            backstory="""You are an expert in API integrations with deep knowledge of REST, GraphQL, 
            and webhooks. You handle authentication, rate limiting, error handling, and response parsing 
            with precision and reliability.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            max_rpm=8
        )
    
    def _create_validation_expert(self) -> Agent:
        """Create validation expert agent"""
        return Agent(
            role="Validation Expert",
            goal="Validate workflow execution results, ensure data integrity, and maintain quality standards",
            backstory="""You are a meticulous validation expert with expertise in quality assurance, 
            data validation, and compliance checking. You ensure all workflow outputs meet specified 
            requirements and standards.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=2,
            max_rpm=12
        )
    
    def _create_error_handler(self) -> Agent:
        """Create error handler agent"""
        return Agent(
            role="Error Handler & Recovery Specialist",
            goal="Handle errors gracefully, implement recovery strategies, and maintain workflow resilience",
            backstory="""You are an expert in error handling and system recovery. You analyze failures, 
            implement fallback strategies, and ensure workflows can recover from errors without data loss.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=True,
            max_iter=2,
            max_rpm=10
        )
    
    def _create_report_generator(self) -> Agent:
        """Create report generator agent"""
        return Agent(
            role="Report Generator",
            goal="Generate comprehensive reports and summaries of workflow execution",
            backstory="""You are a skilled report generator who creates clear, actionable reports from 
            complex workflow executions. You summarize results, highlight key findings, and provide 
            recommendations for improvement.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=1,
            max_rpm=20
        )
    
    def get_agent(self, agent_name: str) -> Optional[Agent]:
        """Get an agent by name"""
        return self.agents.get(agent_name)
    
    def get_agents_for_workflow(self, workflow_type: str) -> List[Agent]:
        """Get appropriate agents for a specific workflow type"""
        agent_mapping = {
            "data_processing": ["data_analyst", "validation_expert"],
            "api_workflow": ["api_specialist", "validation_expert"],
            "validation": ["validation_expert", "report_generator"],
            "complex": ["workflow_orchestrator", "data_analyst", "api_specialist", "validation_expert"],
            "default": ["workflow_orchestrator", "validation_expert"]
        }
        
        agent_names = agent_mapping.get(workflow_type, agent_mapping["default"])
        return [self.agents[name] for name in agent_names if name in self.agents]

# Global enhanced agent manager
enhanced_agent_manager = EnhancedAgentManager()
