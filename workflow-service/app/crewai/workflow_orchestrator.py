"""
CrewAI workflow orchestrator for Flov7 workflow service.
Provides comprehensive multi-agent workflow processing and coordination.
"""

from crewai import Crew, Task
from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime
import json

# Import enhanced components
from app.crewai.enhanced_agents import enhanced_agent_manager
from app.crewai.enhanced_tasks import enhanced_task_manager

# Configure logging
logger = logging.getLogger(__name__)

class CrewAIWorkflowOrchestrator:
    """Comprehensive CrewAI workflow orchestrator for multi-agent processing"""
    
    def __init__(self):
        self.max_execution_time = 300  # 5 minutes
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    async def execute_workflow_with_crewai(self, workflow_data: Dict[str, Any], 
                                         user_id: str, execution_id: str) -> Dict[str, Any]:
        """
        Execute a complete workflow using CrewAI multi-agent system
        
        Args:
            workflow_data: Complete workflow definition
            user_id: User ID for tracking
            execution_id: Execution ID for tracking
            
        Returns:
            Comprehensive execution results
        """
        try:
            logger.info(f"Starting CrewAI workflow execution: {execution_id}")
            
            # Validate workflow structure
            validation_result = await self._validate_workflow_structure(workflow_data)
            if not validation_result["valid"]:
                return self._create_error_result(execution_id, validation_result["issues"])
            
            # Analyze workflow and create execution plan
            execution_plan = await self._create_execution_plan(workflow_data)
            
            # Execute workflow phases
            phase_results = await self._execute_workflow_phases(workflow_data, execution_plan)
            
            # Generate comprehensive results
            final_result = await self._generate_final_result(
                workflow_data, execution_id, user_id, phase_results
            )
            
            logger.info(f"CrewAI workflow execution completed: {execution_id}")
            return final_result
            
        except Exception as e:
            logger.error(f"CrewAI workflow execution failed: {str(e)}")
            return self._create_error_result(execution_id, str(e))
    
    async def execute_ai_task(self, task_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute individual AI task using CrewAI agents for Temporal integration
        
        Args:
            task_config: AI task configuration
            context: Execution context and inputs
            
        Returns:
            AI task execution result
        """
        try:
            agent_type = task_config.get("agent_type", "generic")
            prompt = task_config.get("prompt", "")
            
            logger.info(f"Executing CrewAI task: {agent_type}")
            
            # Get appropriate agent for the task type
            agent = self._get_agent_for_task_type(agent_type)
            if not agent:
                return {
                    "response": "No suitable agent found for task type",
                    "confidence": 0.0,
                    "error": f"Unknown agent type: {agent_type}"
                }
            
            # Create task for this specific AI operation
            from app.crewai.enhanced_tasks import enhanced_task_manager
            
            task = enhanced_task_manager.create_ai_specific_task(
                agent=agent,
                task_type=agent_type,
                prompt=prompt,
                context=context
            )
            
            # Execute task with CrewAI
            from crewai import Crew
            
            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=crewai_config.verbose_mode,
                process="sequential"
            )
            
            result = crew.kickoff()
            
            return {
                "response": str(result),
                "confidence": 0.9,  # CrewAI confidence
                "agent_type": agent_type,
                "metadata": {
                    "task_type": agent_type,
                    "prompt_length": len(prompt),
                    "context_keys": list(context.keys())
                }
            }
            
        except Exception as e:
            logger.error(f"CrewAI task execution failed: {str(e)}")
            return {
                "response": "AI task execution failed",
                "confidence": 0.0,
                "error": str(e),
                "fallback": True
            }

    def _get_agent_for_task_type(self, agent_type: str):
        """Get appropriate agent based on task type"""
        from app.crewai.enhanced_agents import enhanced_agent_manager
        
        agent_mapping = {
            "data_analysis": "data_analyst",
            "api_processing": "api_specialist",
            "validation": "validation_expert",
            "content_generation": "report_generator",
            "workflow_orchestration": "workflow_orchestrator",
            "error_handling": "error_handler",
            "generic": "workflow_orchestrator"
        }
        
        mapped_type = agent_mapping.get(agent_type, "workflow_orchestrator")
        return enhanced_agent_manager.get_agent(mapped_type)

    async def _validate_workflow_structure(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow structure before execution"""
        try:
            nodes = workflow_data.get("nodes", [])
            edges = workflow_data.get("edges", [])
            
            issues = []
            
            # Basic validation
            if not nodes:
                issues.append("No workflow nodes provided")
            
            # Validate node references in edges
            node_ids = {node.get("id") for node in nodes}
            for edge in edges:
                if edge.get("source") not in node_ids:
                    issues.append(f"Edge references non-existent source: {edge.get('source')}")
                if edge.get("target") not in node_ids:
                    issues.append(f"Edge references non-existent target: {edge.get('target')}")
            
            # Check for cycles
            if self._has_cycles(nodes, edges):
                issues.append("Workflow contains cycles")
            
            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "warnings": []
            }
            
        except Exception as e:
            return {"valid": False, "issues": [str(e)], "warnings": []}
    
    def _has_cycles(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> bool:
        """Check if workflow has cycles using DFS"""
        if not edges:
            return False
        
        # Build adjacency list
        graph = {}
        node_ids = {node.get("id") for node in nodes}
        
        for node_id in node_ids:
            graph[node_id] = []
        
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            if source in graph and target in graph:
                graph[source].append(target)
        
        # DFS cycle detection
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if dfs(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node_id in node_ids:
            if node_id not in visited:
                if dfs(node_id):
                    return True
        
        return False
    
    async def _create_execution_plan(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive execution plan for multi-agent processing"""
        try:
            nodes = workflow_data.get("nodes", [])
            edges = workflow_data.get("edges", [])
            
            # Build execution order
            execution_order = self._build_execution_order(nodes, edges)
            
            # Group nodes by phases
            phases = self._group_nodes_by_phases(nodes, execution_order)
            
            return {
                "execution_order": execution_order,
                "phases": phases,
                "parallel_groups": self._identify_parallel_groups(nodes, edges),
                "critical_path": self._identify_critical_path(nodes, edges)
            }
            
        except Exception as e:
            logger.error(f"Failed to create execution plan: {str(e)}")
            return {"execution_order": [], "phases": [], "parallel_groups": [], "critical_path": []}
    
    def _build_execution_order(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[str]:
        """Build execution order using topological sort"""
        if not edges:
            return [node["id"] for node in nodes]
        
        # Build graph and in-degree
        graph = {}
        in_degree = {}
        node_ids = {node["id"] for node in nodes}
        
        for node_id in node_ids:
            graph[node_id] = []
            in_degree[node_id] = 0
        
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            if source in graph and target in graph:
                graph[source].append(target)
                in_degree[target] += 1
        
        # Topological sort
        queue = [node_id for node_id in node_ids if in_degree[node_id] == 0]
        execution_order = []
        
        while queue:
            current = queue.pop(0)
            execution_order.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return execution_order
    
    def _group_nodes_by_phases(self, nodes: List[Dict[str, Any]], execution_order: List[str]) -> List[Dict[str, Any]]:
        """Group nodes into execution phases"""
        phases = []
        current_phase = []
        
        for node_id in execution_order:
            node = next((n for n in nodes if n["id"] == node_id), None)
            if node:
                current_phase.append(node)
                
                # Create new phase for certain node types or after specific conditions
                if node.get("type") in ["api_call", "database"] or len(current_phase) >= 3:
                    phases.append({
                        "phase_id": len(phases),
                        "nodes": current_phase,
                        "type": self._determine_phase_type(current_phase)
                    })
                    current_phase = []
        
        if current_phase:
            phases.append({
                "phase_id": len(phases),
                "nodes": current_phase,
                "type": self._determine_phase_type(current_phase)
            })
        
        return phases
    
    def _determine_phase_type(self, nodes: List[Dict[str, Any]]) -> str:
        """Determine the type of execution phase"""
        node_types = [node.get("type", "unknown") for node in nodes]
        
        if any(nt in ["api_call", "webhook"] for nt in node_types):
            return "external_integration"
        elif any(nt in ["data_processor", "transform"] for nt in node_types):
            return "data_processing"
        elif any(nt in ["condition", "validation"] for nt in node_types):
            return "validation"
        else:
            return "general_processing"
    
    def _identify_parallel_groups(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[List[str]]:
        """Identify groups of nodes that can be executed in parallel"""
        # Simple implementation - nodes with no dependencies can run in parallel
        node_ids = {node["id"] for node in nodes}
        dependencies = {node_id: set() for node_id in node_ids}
        
        for edge in edges:
            target = edge.get("target")
            source = edge.get("source")
            if target in dependencies and source in dependencies:
                dependencies[target].add(source)
        
        # Find independent nodes
        independent_nodes = [node_id for node_id, deps in dependencies.items() if not deps]
        
        return [independent_nodes] if independent_nodes else []
    
    def _identify_critical_path(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[str]:
        """Identify the critical path in the workflow"""
        # Simplified implementation - longest path through dependencies
        execution_order = self._build_execution_order(nodes, edges)
        return execution_order  # For now, use full execution order
    
    async def _execute_workflow_phases(self, workflow_data: Dict[str, Any], 
                                     execution_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute workflow phases using CrewAI"""
        phase_results = []
        
        try:
            phases = execution_plan.get("phases", [])
            
            for phase in phases:
                phase_result = await self._execute_phase_with_crewai(phase, workflow_data)
                phase_results.append(phase_result)
                
                # Stop on error
                if phase_result.get("status") == "failed":
                    break
            
            return phase_results
            
        except Exception as e:
            logger.error(f"Failed to execute workflow phases: {str(e)}")
            return [{"status": "failed", "error": str(e)}]
    
    async def _execute_phase_with_crewai(self, phase: Dict[str, Any], 
                                       workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single phase using CrewAI"""
        try:
            # Create tasks for this phase
            tasks = enhanced_task_manager.create_workflow_specific_tasks({
                "nodes": phase["nodes"],
                "type": phase["type"]
            })
            
            if not tasks:
                return {"status": "skipped", "message": "No tasks to execute"}
            
            # Get appropriate agents
            agents = enhanced_agent_manager.get_agents_for_workflow(phase["type"])
            
            # Create crew
            crew = Crew(
                agents=agents,
                tasks=tasks,
                verbose=True,
                process="sequential",
                memory=True,
                max_rpm=10,
                max_execution_time=120
            )
            
            # Execute crew
            phase_input = {
                "phase_data": phase,
                "workflow_context": workflow_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: crew.kickoff(inputs=phase_input)
            )
            
            return {
                "status": "completed",
                "phase_id": phase["phase_id"],
                "result": str(result),
                "nodes_executed": len(phase["nodes"]),
                "agents_used": len(agents),
                "execution_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "phase_id": phase["phase_id"],
                "error": str(e),
                "execution_time": datetime.utcnow().isoformat()
            }
    
    async def _generate_final_result(self, workflow_data: Dict[str, Any], 
                                   execution_id: str, user_id: str, 
                                   phase_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive final results"""
        try:
            # Calculate summary metrics
            total_phases = len(phase_results)
            completed_phases = len([r for r in phase_results if r.get("status") == "completed"])
            failed_phases = len([r for r in phase_results if r.get("status") == "failed"])
            
            # Generate execution summary
            execution_summary = {
                "workflow_name": workflow_data.get("name", "Unknown"),
                "workflow_id": workflow_data.get("id"),
                "execution_id": execution_id,
                "user_id": user_id,
                "status": "completed" if failed_phases == 0 else "failed",
                "total_phases": total_phases,
                "completed_phases": completed_phases,
                "failed_phases": failed_phases,
                "phase_results": phase_results,
                "execution_method": "crewai_multi_agent",
                "timestamp": datetime.utcnow().isoformat(),
                "performance_metrics": {
                    "total_execution_time": sum(
                        1 for r in phase_results if r.get("execution_time")
                    ),
                    "successful_phase_ratio": completed_phases / max(total_phases, 1),
                    "multi_agent_coordination": True
                }
            }
            
            return execution_summary
            
        except Exception as e:
            return self._create_error_result(execution_id, str(e))
    
    def _create_error_result(self, execution_id: str, error_message: str) -> Dict[str, Any]:
        """Create error result structure"""
        return {
            "execution_id": execution_id,
            "status": "failed",
            "error_message": error_message,
            "timestamp": datetime.utcnow().isoformat(),
            "execution_method": "crewai_multi_agent"
        }

# Global orchestrator instance
crewai_orchestrator = CrewAIWorkflowOrchestrator()
