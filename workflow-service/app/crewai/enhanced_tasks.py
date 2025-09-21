"""
Enhanced CrewAI tasks for Flov7 workflow service with multi-agent coordination.
Provides comprehensive task definitions for workflow processing.
"""

from crewai import Task, Agent
from typing import Optional, Dict, Any, List
from app.crewai.enhanced_agents import enhanced_agent_manager
import logging
import json
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedTaskManager:
    """Enhanced manager for CrewAI tasks with workflow-specific capabilities"""
    
    def __init__(self):
        self.tasks = {}
        self._initialize_enhanced_tasks()
    
    def _initialize_enhanced_tasks(self):
        """Initialize enhanced tasks with specific workflow capabilities"""
        try:
            # Get enhanced agents
            orchestrator = enhanced_agent_manager.get_agent("workflow_orchestrator")
            data_analyst = enhanced_agent_manager.get_agent("data_analyst")
            api_specialist = enhanced_agent_manager.get_agent("api_specialist")
            validation_expert = enhanced_agent_manager.get_agent("validation_expert")
            error_handler = enhanced_agent_manager.get_agent("error_handler")
            report_generator = enhanced_agent_manager.get_agent("report_generator")
            
            if not all([orchestrator, data_analyst, api_specialist, validation_expert]):
                logger.warning("Some enhanced agents not available, using basic tasks")
                return
            
            # Define enhanced tasks
            self.tasks = {
                "analyze_workflow_structure": self._create_workflow_analysis_task(orchestrator),
                "process_api_data": self._create_api_processing_task(api_specialist),
                "transform_data": self._create_data_transformation_task(data_analyst),
                "validate_workflow_output": self._create_validation_task(validation_expert),
                "handle_execution_errors": self._create_error_handling_task(error_handler),
                "generate_execution_report": self._create_report_generation_task(report_generator),
                "coordinate_multi_agent_workflow": self._create_coordination_task(orchestrator)
            }
            
            logger.info("Enhanced CrewAI tasks initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize enhanced tasks: {str(e)}")
    
    def _create_workflow_analysis_task(self, agent) -> Task:
        """Create workflow analysis task"""
        return Task(
            description="""Analyze the provided workflow structure, identify dependencies between nodes, 
            determine optimal execution order, and create a comprehensive execution plan. Consider 
            resource constraints, potential bottlenecks, and parallelization opportunities.""",
            agent=agent,
            expected_output="""Detailed workflow analysis including:
            - Execution order with dependencies
            - Resource requirements
            - Risk assessment
            - Optimization recommendations
            - Parallel execution opportunities""",
            tools=[]
        )
    
    def _create_api_processing_task(self, agent) -> Task:
        """Create API processing task"""
        return Task(
            description="""Execute API calls as defined in the workflow, handle authentication, 
            rate limiting, error responses, and data transformation. Ensure proper error handling 
            and retry mechanisms are in place.""",
            agent=agent,
            expected_output="""API execution results including:
            - Response data (parsed and structured)
            - Status codes and headers
            - Error details if any
            - Performance metrics
            - Data validation results""",
            tools=[]
        )
    
    def _create_data_transformation_task(self, agent) -> Task:
        """Create data transformation task"""
        return Task(
            description="""Transform data according to workflow specifications, apply business logic, 
            validate data integrity, and ensure output format compliance. Handle edge cases and 
            provide detailed transformation logs.""",
            agent=agent,
            expected_output="""Transformed data including:
            - Original vs transformed data comparison
            - Applied transformations log
            - Data validation results
            - Quality metrics
            - Error handling details""",
            tools=[]
        )
    
    def _create_validation_task(self, agent) -> Task:
        """Create validation task"""
        return Task(
            description="""Comprehensively validate all workflow outputs against requirements, 
            check data integrity, ensure compliance with business rules, and provide detailed 
            validation reports with pass/fail status for each component.""",
            agent=agent,
            expected_output="""Validation report including:
            - Pass/fail status for each validation point
            - Detailed error descriptions
            - Compliance checklist
            - Quality metrics
            - Recommendations for fixes""",
            tools=[]
        )
    
    def _create_error_handling_task(self, agent) -> Task:
        """Create error handling task"""
        return Task(
            description="""Handle workflow execution errors gracefully, implement recovery strategies, 
            log detailed error information, and provide actionable recommendations for preventing 
            similar issues in future executions.""",
            agent=agent,
            expected_output="""Error handling report including:
            - Error analysis and root cause
            - Recovery actions taken
            - Fallback strategies implemented
            - Prevention recommendations
            - System health assessment""",
            tools=[]
        )
    
    def _create_report_generation_task(self, agent) -> Task:
        """Create report generation task"""
        return Task(
            description="""Generate comprehensive execution reports with key metrics, insights, 
            performance data, and actionable recommendations. Include visual summaries where applicable.""",
            agent=agent,
            expected_output="""Comprehensive execution report including:
            - Executive summary
            - Detailed execution timeline
            - Performance metrics and KPIs
            - Key insights and findings
            - Recommendations for improvement
            - Next steps and action items""",
            tools=[]
        )
    
    def _create_coordination_task(self, agent) -> Task:
        """Create coordination task"""
        return Task(
            description="""Coordinate multi-agent workflow execution, manage task dependencies, 
            handle inter-agent communication, and ensure smooth workflow progression. Monitor 
            execution status and adjust plans as needed.""",
            agent=agent,
            expected_output="""Coordination summary including:
            - Task execution sequence
            - Agent collaboration log
            - Dependency management
            - Performance optimization
            - Final execution status""",
            tools=[]
        )
    
    def create_workflow_specific_tasks(self, workflow_data: Dict[str, Any]) -> List[Task]:
        """Create tasks specific to the workflow being executed"""
        try:
            workflow_tasks = []
            nodes = workflow_data.get("nodes", [])
            
            if not nodes:
                return []
            
            # Create tasks based on workflow nodes
            for i, node in enumerate(nodes):
                node_type = node.get("type", "unknown")
                node_data = node.get("data", {})
                
                # Get appropriate agent and task
                agent = self._get_agent_for_node_type(node_type)
                task = self._get_task_for_node_type(node_type, agent, node_data)
                
                if task:
                    workflow_tasks.append(task)
            
                workflow_tasks.append(self.tasks["coordinate_multi_agent_workflow"])
                workflow_tasks.append(self.tasks["validate_workflow_output"])
                workflow_tasks.append(self.tasks["generate_execution_report"])
            
            return workflow_tasks
            
        except Exception as e:
            logger.error(f"Failed to create workflow-specific tasks: {str(e)}")
            return []

    def create_ai_specific_task(self, agent, task_type: str, prompt: str, context: Dict[str, Any]) -> Task:
        """
        Create a specific AI task for Temporal integration
        
        Args:
            agent: CrewAI agent to execute the task
            task_type: Type of AI task
            prompt: Task prompt/description
            context: Execution context
            
        Returns:
            CrewAI Task object
        """
        try:
            # Create task description based on type
            task_descriptions = {
                "data_analysis": f"Analyze the provided data: {prompt}",
                "api_processing": f"Process API data based on: {prompt}",
                "validation": f"Validate the following: {prompt}",
                "content_generation": f"Generate content for: {prompt}",
                "workflow_orchestration": f"Orchestrate workflow step: {prompt}",
                "error_handling": f"Handle error scenario: {prompt}",
                "generic": f"Execute AI task: {prompt}"
            }
            
            description = task_descriptions.get(task_type, f"Execute: {prompt}")
            
            # Include context in task
            context_str = f"Context: {context}" if context else ""
            full_description = f"{description}\n{context_str}"
            
            return Task(
                description=full_description,
                agent=agent,
                expected_output="Complete task result with relevant data or insights"
            )
            
        except Exception as e:
            logger.error(f"Failed to create AI-specific task: {str(e)}")
            
            # Return basic task as fallback
            return Task(
                description=f"Execute AI task: {prompt}",
                agent=agent,
                expected_output="Task completion result"
            )
    
    def _create_node_specific_task(self, node: Dict[str, Any], node_data: Dict[str, Any], agents: List) -> Optional[Task]:
        """Create a task specific to a workflow node"""
        try:
            node_type = node.get("type", "unknown")
            node_id = node.get("id", f"node_{datetime.now().timestamp()}")
            
            # Select appropriate agent for this node type
            agent = self._select_agent_for_node_type(node_type, agents)
            if not agent:
                return None
            
            # Generate task description based on node type and data
            task_description = self._generate_node_task_description(node, node_data)
            expected_output = self._generate_node_expected_output(node, node_data)
            
            return Task(
                description=task_description,
                agent=agent,
                expected_output=expected_output
            )
            
        except Exception as e:
            logger.error(f"Failed to create node-specific task: {str(e)}")
            return None
    
    def _select_agent_for_node_type(self, node_type: str, agents: List) -> Optional[Agent]:
        """Select the most appropriate agent for a node type"""
        agent_mapping = {
            "api_call": "api_specialist",
            "data_processor": "data_analyst",
            "transform": "data_analyst",
            "condition": "validation_expert",
            "validation": "validation_expert",
            "report": "report_generator",
            "error": "error_handler",
            "default": "workflow_orchestrator"
        }
        
        agent_name = agent_mapping.get(node_type, "default")
        
        # Find the agent in the provided list
        for agent in agents:
            if hasattr(agent, 'role') and agent_name in str(agent.role).lower():
                return agent
        
        return agents[0] if agents else None
    
    def _generate_node_task_description(self, node: Dict[str, Any], node_data: Dict[str, Any]) -> str:
        """Generate task description based on node configuration"""
        node_type = node.get("type", "unknown")
        node_label = node_data.get("label", f"Node {node.get('id', 'unknown')}")
        
        base_descriptions = {
            "api_call": f"Execute API call for {node_label}: {node_data.get('url', 'unknown endpoint')}",
            "transform": f"Transform data for {node_label} using {node_data.get('transform_type', 'mapping')}",
            "condition": f"Evaluate condition for {node_label}: {node_data.get('condition', 'unknown condition')}",
            "delay": f"Execute delay operation for {node_label}: {node_data.get('delay_seconds', 0)} seconds",
            "database": f"Perform database operation for {node_label}: {node_data.get('operation', 'unknown operation')}",
            "webhook": f"Send webhook for {node_label} to {node_data.get('url', 'unknown endpoint')}",
            "ai_agent": f"Execute AI agent task for {node_label}: {node_data.get('prompt', 'unknown prompt')}"
        }
        
        return base_descriptions.get(node_type, f"Execute {node_type} task for {node_label}")
    
    def _generate_node_expected_output(self, node: Dict[str, Any], node_data: Dict[str, Any]) -> str:
        """Generate expected output based on node type"""
        node_type = node.get("type", "unknown")
        
        base_outputs = {
            "api_call": "API response data with status and headers",
            "transform": "Transformed data in specified format",
            "condition": "Boolean result of condition evaluation",
            "delay": "Confirmation of delay completion",
            "database": "Database operation results",
            "webhook": "Webhook delivery confirmation",
            "ai_agent": "AI agent response and insights"
        }
        
        return base_outputs.get(node_type, f"Task completion status and results for {node_type}")
    
    def get_task(self, task_name: str) -> Optional[Task]:
        """Get a task by name"""
        return self.tasks.get(task_name)
    
    def get_all_tasks(self) -> dict:
        """Get all tasks"""
        return self.tasks

# Global enhanced task manager
enhanced_task_manager = EnhancedTaskManager()
