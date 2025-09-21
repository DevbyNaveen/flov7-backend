"""
Advanced AI prompts for sophisticated workflow generation.
Provides enhanced prompting strategies for better workflow creation.
"""

from typing import Dict, Any, List, Optional
import json


class AdvancedPromptEngine:
    """Advanced prompt engineering for workflow generation"""
    
    def __init__(self):
        self.primitives_info = self._get_primitives_info()
        self.workflow_patterns = self._get_workflow_patterns()
    
    def _get_primitives_info(self) -> Dict[str, Any]:
        """Get detailed information about the 5 primitives"""
        return {
            "trigger": {
                "description": "Initiates workflow execution based on events or conditions",
                "examples": ["HTTP webhook", "scheduled timer", "file upload", "database change"],
                "capabilities": ["event detection", "condition monitoring", "data ingestion"],
                "best_practices": ["Use specific trigger conditions", "Handle edge cases", "Validate input data"]
            },
            "action": {
                "description": "Performs operations and transformations on data",
                "examples": ["API call", "data transformation", "file processing", "email sending"],
                "capabilities": ["data manipulation", "external service integration", "computation"],
                "best_practices": ["Handle errors gracefully", "Use appropriate timeouts", "Log operations"]
            },
            "connection": {
                "description": "Manages data flow and communication between components",
                "examples": ["API connector", "database connection", "message queue", "webhook"],
                "capabilities": ["data routing", "protocol translation", "authentication"],
                "best_practices": ["Secure credentials", "Handle connection failures", "Use connection pooling"]
            },
            "condition": {
                "description": "Implements decision logic and branching in workflows",
                "examples": ["if-then logic", "data validation", "approval gates", "routing rules"],
                "capabilities": ["logical evaluation", "data filtering", "flow control"],
                "best_practices": ["Clear condition logic", "Handle null values", "Provide fallback paths"]
            },
            "data": {
                "description": "Handles data storage, retrieval, and management",
                "examples": ["database operations", "file storage", "cache management", "data validation"],
                "capabilities": ["data persistence", "data retrieval", "data transformation"],
                "best_practices": ["Validate data integrity", "Handle large datasets", "Implement proper indexing"]
            }
        }
    
    def _get_workflow_patterns(self) -> Dict[str, Any]:
        """Get common workflow patterns and templates"""
        return {
            "data_processing": {
                "description": "Process and transform data from various sources",
                "typical_flow": ["trigger", "data", "action", "condition", "data"],
                "use_cases": ["ETL pipelines", "data validation", "report generation"]
            },
            "api_integration": {
                "description": "Integrate with external APIs and services",
                "typical_flow": ["trigger", "connection", "action", "condition", "data"],
                "use_cases": ["CRM sync", "payment processing", "notification systems"]
            },
            "automation": {
                "description": "Automate repetitive tasks and processes",
                "typical_flow": ["trigger", "condition", "action", "data"],
                "use_cases": ["email automation", "file processing", "task scheduling"]
            },
            "monitoring": {
                "description": "Monitor systems and trigger alerts",
                "typical_flow": ["trigger", "condition", "action", "connection"],
                "use_cases": ["system monitoring", "error alerting", "performance tracking"]
            },
            "approval_workflow": {
                "description": "Implement approval and review processes",
                "typical_flow": ["trigger", "data", "condition", "action", "connection"],
                "use_cases": ["document approval", "expense approval", "content review"]
            }
        }
    
    def generate_system_prompt(self) -> str:
        """Generate comprehensive system prompt for workflow generation"""
        return f"""You are an expert AI workflow architect specializing in the Flov7 5-primitives system. Your task is to create sophisticated, production-ready workflows from natural language descriptions.

## 5-PRIMITIVES SYSTEM OVERVIEW:

{json.dumps(self.primitives_info, indent=2)}

## WORKFLOW PATTERNS:

{json.dumps(self.workflow_patterns, indent=2)}

## WORKFLOW GENERATION RULES:

1. **Structure Requirements:**
   - Every workflow must have: name, description, nodes, edges
   - Nodes must have: id, type, position {{x, y}}, data
   - Edges must have: id, source, target
   - Use only the 5 primitive types: trigger, action, connection, condition, data

2. **Design Principles:**
   - Start with a trigger primitive
   - Ensure logical flow between primitives
   - Handle error cases and edge conditions
   - Optimize for performance and reliability
   - Include proper validation and logging

3. **Best Practices:**
   - Use descriptive names and labels
   - Implement proper error handling
   - Consider scalability and maintainability
   - Include monitoring and observability
   - Follow security best practices

4. **Output Format:**
   Return a valid JSON workflow definition with the following structure:
   ```json
   {{
     "name": "Workflow Name",
     "description": "Detailed workflow description",
     "nodes": [
       {{
         "id": "unique_node_id",
         "type": "primitive_type",
         "position": {{"x": 100, "y": 100}},
         "data": {{
           "label": "Node Label",
           "config": {{
             // Primitive-specific configuration
           }}
         }}
       }}
     ],
     "edges": [
       {{
         "id": "unique_edge_id",
         "source": "source_node_id",
         "target": "target_node_id"
       }}
     ],
     "metadata": {{
       "complexity": "low|medium|high",
       "estimated_execution_time": "time_in_seconds",
       "required_integrations": ["list", "of", "services"],
       "tags": ["tag1", "tag2"]
     }}
   }}
   ```

## ADVANCED CAPABILITIES:

- **Context Awareness:** Consider user's industry, use case, and technical requirements
- **Error Handling:** Include comprehensive error handling and recovery mechanisms
- **Scalability:** Design workflows that can handle varying loads and data volumes
- **Security:** Implement proper authentication, authorization, and data protection
- **Monitoring:** Include logging, metrics, and alerting capabilities
- **Integration:** Seamlessly connect with popular services and APIs

Generate workflows that are not just functional, but production-ready, scalable, and maintainable."""

    def generate_user_prompt(self, user_request: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate enhanced user prompt with context"""
        context = context or {}
        
        prompt_parts = [
            f"Create a workflow for: {user_request}",
            ""
        ]
        
        # Add context information
        if context.get("user_industry"):
            prompt_parts.append(f"Industry context: {context['user_industry']}")
        
        if context.get("technical_level"):
            prompt_parts.append(f"Technical level: {context['technical_level']}")
        
        if context.get("existing_integrations"):
            prompt_parts.append(f"Available integrations: {', '.join(context['existing_integrations'])}")
        
        if context.get("performance_requirements"):
            prompt_parts.append(f"Performance requirements: {context['performance_requirements']}")
        
        if context.get("security_requirements"):
            prompt_parts.append(f"Security requirements: {context['security_requirements']}")
        
        # Add specific requirements
        prompt_parts.extend([
            "",
            "Requirements:",
            "- Create a complete, production-ready workflow",
            "- Use appropriate primitives for each step",
            "- Include proper error handling and validation",
            "- Optimize for performance and reliability",
            "- Follow security best practices",
            "- Include monitoring and logging capabilities",
            "",
            "Focus on creating a workflow that is:",
            "1. Functionally complete and correct",
            "2. Scalable and maintainable",
            "3. Secure and robust",
            "4. Well-documented and clear"
        ])
        
        return "\n".join(prompt_parts)
    
    def enhance_workflow_with_metadata(self, workflow: Dict[str, Any], user_request: str) -> Dict[str, Any]:
        """Enhance generated workflow with additional metadata"""
        
        # Calculate complexity based on node count and connections
        node_count = len(workflow.get("nodes", []))
        edge_count = len(workflow.get("edges", []))
        
        if node_count <= 3:
            complexity = "low"
        elif node_count <= 7:
            complexity = "medium"
        else:
            complexity = "high"
        
        # Estimate execution time based on primitives
        base_time = 5  # Base 5 seconds
        time_per_node = 2  # 2 seconds per node
        estimated_time = base_time + (node_count * time_per_node)
        
        # Extract required integrations from node configurations
        required_integrations = set()
        for node in workflow.get("nodes", []):
            node_data = node.get("data", {})
            config = node_data.get("config", {})
            
            # Look for common integration patterns
            if "api" in str(config).lower():
                required_integrations.add("API")
            if "database" in str(config).lower():
                required_integrations.add("Database")
            if "email" in str(config).lower():
                required_integrations.add("Email")
            if "webhook" in str(config).lower():
                required_integrations.add("Webhook")
        
        # Generate tags based on workflow content
        tags = []
        request_lower = user_request.lower()
        
        if any(word in request_lower for word in ["data", "process", "transform"]):
            tags.append("data-processing")
        if any(word in request_lower for word in ["api", "integration", "connect"]):
            tags.append("integration")
        if any(word in request_lower for word in ["automate", "automation", "schedule"]):
            tags.append("automation")
        if any(word in request_lower for word in ["monitor", "alert", "notify"]):
            tags.append("monitoring")
        if any(word in request_lower for word in ["approve", "approval", "review"]):
            tags.append("approval")
        
        # Add metadata to workflow
        workflow["metadata"] = {
            "complexity": complexity,
            "estimated_execution_time": estimated_time,
            "required_integrations": list(required_integrations),
            "tags": tags,
            "node_count": node_count,
            "edge_count": edge_count,
            "generated_from": user_request[:100] + "..." if len(user_request) > 100 else user_request
        }
        
        return workflow
    
    def validate_workflow_quality(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and score workflow quality"""
        issues = []
        score = 100
        
        # Check required fields
        required_fields = ["name", "description", "nodes", "edges"]
        for field in required_fields:
            if field not in workflow:
                issues.append(f"Missing required field: {field}")
                score -= 20
        
        # Validate nodes
        nodes = workflow.get("nodes", [])
        if not nodes:
            issues.append("Workflow has no nodes")
            score -= 30
        
        valid_types = {"trigger", "action", "connection", "condition", "data"}
        for i, node in enumerate(nodes):
            if "type" not in node or node["type"] not in valid_types:
                issues.append(f"Node {i} has invalid type")
                score -= 10
            
            if "position" not in node or "x" not in node.get("position", {}) or "y" not in node.get("position", {}):
                issues.append(f"Node {i} missing position coordinates")
                score -= 5
        
        # Check for trigger node
        has_trigger = any(node.get("type") == "trigger" for node in nodes)
        if not has_trigger:
            issues.append("Workflow should start with a trigger primitive")
            score -= 15
        
        # Validate edges
        edges = workflow.get("edges", [])
        node_ids = {node.get("id") for node in nodes}
        
        for i, edge in enumerate(edges):
            if "source" not in edge or "target" not in edge:
                issues.append(f"Edge {i} missing source or target")
                score -= 10
            elif edge["source"] not in node_ids or edge["target"] not in node_ids:
                issues.append(f"Edge {i} references non-existent nodes")
                score -= 10
        
        # Check workflow connectivity
        if len(nodes) > 1 and len(edges) == 0:
            issues.append("Multi-node workflow has no connections")
            score -= 20
        
        return {
            "score": max(0, score),
            "issues": issues,
            "quality": "excellent" if score >= 90 else "good" if score >= 70 else "fair" if score >= 50 else "poor"
        }


# Global advanced prompt engine instance
advanced_prompt_engine = AdvancedPromptEngine()
