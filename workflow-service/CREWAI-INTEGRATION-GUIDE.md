# CrewAI Integration Guide - Flov7 Workflow Service

## Overview

This guide provides comprehensive instructions for using the CrewAI multi-agent integration in the Flov7 workflow service. The integration provides intelligent multi-agent workflow processing with specialized AI agents for different workflow tasks.

## Architecture

### Components

1. **Enhanced Agents** (`app/crewai/enhanced_agents.py`) - Specialized AI agents with specific roles
2. **Enhanced Tasks** (`app/crewai/enhanced_tasks.py`) - Workflow-specific task definitions
3. **Workflow Orchestrator** (`app/crewai/workflow_orchestrator.py`) - Multi-agent coordination logic
4. **Configuration** (`app/crewai/config.py`) - Centralized CrewAI settings

### Agent Roles

- **Workflow Orchestrator**: Designs and coordinates complex multi-agent workflows
- **Data Analyst**: Processes and transforms data according to workflow requirements
- **API Specialist**: Executes API calls and handles external service integrations
- **Validation Expert**: Validates workflow outputs and ensures data integrity
- **Error Handler**: Manages errors gracefully and implements recovery strategies
- **Report Generator**: Generates comprehensive execution reports

## Setup Instructions

### 1. Environment Configuration

Add to your `.env` file:

```bash
# CrewAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# Agent Configuration
CREWAI_MAX_ITERATIONS=3
CREWAI_MAX_RPM=10
CREWAI_AGENT_TIMEOUT=120
CREWAI_ALLOW_DELEGATION=true

# Workflow Configuration
CREWAI_MAX_EXECUTION_TIME=300
CREWAI_MAX_RETRIES=3
CREWAI_RETRY_DELAY=2

# Feature Flags
ENABLE_CREWAI=true
ENABLE_ENHANCED_AGENTS=true
```

### 2. Dependencies

Ensure these packages are installed:

```bash
pip install crewai langchain-openai
```

## Usage Examples

### 1. Basic Workflow Execution

```python
import asyncio
from app.crewai.workflow_orchestrator import crewai_orchestrator

async def execute_with_crewai():
    # Define a workflow
    workflow_data = {
        "id": "crewai-demo-001",
        "name": "CrewAI Demo Workflow",
        "type": "api_workflow",
        "nodes": [
            {
                "id": "fetch-data",
                "type": "api_call",
                "data": {
                    "url": "https://jsonplaceholder.typicode.com/posts/1",
                    "method": "GET"
                }
            },
            {
                "id": "process-data",
                "type": "transform",
                "data": {
                    "transform_type": "mapping",
                    "mapping": {
                        "title": "inputs.title",
                        "userId": "inputs.userId"
                    }
                }
            },
            {
                "id": "validate",
                "type": "validation",
                "data": {
                    "rules": ["title_required", "userId_positive"]
                }
            }
        ],
        "edges": [
            {"source": "fetch-data", "target": "process-data"},
            {"source": "process-data", "target": "validate"}
        ]
    }
    
    # Execute with CrewAI
    result = await crewai_orchestrator.execute_workflow_with_crewai(
        workflow_data, "user123", "execution-001"
    )
    
    print(f"Execution status: {result['status']}")
    if result['status'] == 'completed':
        print(f"Phases executed: {result['total_phases']}")
```

### 2. Agent Selection for Workflows

```python
from app.crewai.enhanced_agents import enhanced_agent_manager

# Get agents for different workflow types
api_agents = enhanced_agent_manager.get_agents_for_workflow("api_workflow")
data_agents = enhanced_agent_manager.get_agents_for_workflow("data_processing")
complex_agents = enhanced_agent_manager.get_agents_for_workflow("complex")

print(f"API workflow agents: {[a.role for a in api_agents]}")
print(f"Data processing agents: {[a.role for a in data_agents]}")
```

### 3. Custom Task Creation

```python
from app.crewai.enhanced_tasks import enhanced_task_manager

# Create custom tasks for a workflow
workflow_data = {
    "nodes": [
        {"id": "custom-task-1", "type": "api_call", "data": {"url": "https://api.example.com"}},
        {"id": "custom-task-2", "type": "transform", "data": {"transform_type": "filter"}}
    ]
}

tasks = enhanced_task_manager.create_workflow_specific_tasks(workflow_data)
print(f"Created {len(tasks)} custom tasks")
```

## Workflow Types

### Supported Workflow Types

1. **api_workflow**: Focuses on API integrations and data fetching
   - Uses: API Specialist, Validation Expert
   - Best for: External service integrations

2. **data_processing**: Emphasizes data transformation and analysis
   - Uses: Data Analyst, Validation Expert
   - Best for: ETL operations and data pipelines

3. **validation**: Centers on quality assurance and validation
   - Uses: Validation Expert, Report Generator
   - Best for: Compliance and quality checks

4. **complex**: Full multi-agent orchestration
   - Uses: All agents with Workflow Orchestrator
   - Best for: Complex business workflows

## Configuration Options

### Agent Configuration

```python
from app.crewai.config import crewai_config

# View current configuration
print(f"Max iterations: {crewai_config.max_iterations}")
print(f"Max RPM: {crewai_config.max_rpm}")
print(f"Allow delegation: {crewai_config.allow_delegation}")

# Check configuration validity
config_valid = crewai_config.validate_config()
if config_valid["valid"]:
    print("Configuration is valid")
else:
    print(f"Configuration issues: {config_valid['issues']}")
```

### Workflow Execution Settings

- **max_execution_time**: Maximum time for workflow execution (default: 300s)
- **max_retries**: Number of retry attempts (default: 3)
- **retry_delay**: Delay between retries in seconds (default: 2)
- **enable_memory**: Enable conversation memory (default: true)
- **verbose_mode**: Enable detailed logging (default: true)

## Error Handling

### Graceful Degradation

The CrewAI integration includes automatic fallback to local execution if multi-agent processing fails:

```python
# The executor automatically falls back to local execution
try:
    result = await executor._execute_with_crewai(workflow_data, user_id, execution_id)
    if not result:
        # Fallback to local execution
        result = await executor._execute_locally(workflow_data, user_id, execution_id)
except Exception as e:
    logger.error(f"CrewAI execution failed: {e}")
```

### Error Types

1. **Configuration Errors**: Invalid API keys or settings
2. **Execution Timeouts**: Workflows taking too long
3. **Agent Failures**: Individual agent execution failures
4. **Validation Errors**: Workflow structure issues
5. **Network Errors**: External service communication failures

## Monitoring and Observability

### Execution Metrics

Each CrewAI workflow execution provides detailed metrics:

```python
result = await crewai_orchestrator.execute_workflow_with_crewai(workflow_data, user_id, execution_id)

print(f"Workflow: {result['workflow_name']}")
print(f"Status: {result['status']}")
print(f"Phases: {result['total_phases']}")
print(f"Completed: {result['completed_phases']}")
print(f"Performance: {result.get('performance_metrics', {})}")
```

### Logging

CrewAI provides comprehensive logging:

- **Agent Actions**: Individual agent decisions and actions
- **Task Progress**: Task completion status and results
- **Error Details**: Detailed error information and context
- **Performance Metrics**: Execution time and resource usage

## Integration with Temporal

### Combined Usage

CrewAI can be used alongside Temporal for hybrid workflow execution:

```python
# Temporal handles orchestration, CrewAI handles intelligent processing
from app.temporal.client import get_temporal_client
from app.temporal.workflows import WorkflowExecution

# Temporal client with CrewAI integration
async def execute_hybrid_workflow(workflow_data, user_id, execution_id):
    temporal_client = await get_temporal_client()
    
    if temporal_client:
        # Use Temporal orchestration with CrewAI agents
        handle = await temporal_client.start_workflow(
            WorkflowExecution.run,
            workflow_data,
            id=execution_id,
            task_queue="flov7-workflow-task-queue"
        )
        
        result = await handle.result()
        return result
    else:
        # Fallback to direct CrewAI execution
        return await crewai_orchestrator.execute_workflow_with_crewai(
            workflow_data, user_id, execution_id
        )
```

## Testing

### Integration Tests

Run comprehensive CrewAI tests:

```bash
# Run all CrewAI integration tests
python test-crewai-integration.py

# Expected output:
# ============================================================
# CREWAI INTEGRATION TESTS
# ============================================================
# 1. Testing enhanced agent initialization...
# ✓ All enhanced agents initialized successfully
# 2. Testing enhanced task initialization...
# ✓ All enhanced tasks initialized successfully
# 3. Testing workflow validation...
# ✓ Valid workflow structure accepted
# 4. Testing invalid workflow detection...
# ✓ Invalid workflow (cycle) correctly detected
# 5. Testing execution plan creation...
# ✓ Execution plan created successfully
# 6. Testing node-specific task creation...
# ✓ Node-specific tasks created successfully
# 7. Testing simple workflow simulation...
# ✓ Simple workflow simulation completed
# 8. Testing agent selection...
# ✓ Agent selection working correctly
# 9. Testing error handling...
# ✓ Error handling for empty workflow working
#
# ============================================================
# CREWAI TEST RESULTS: 9/9 passed
# ============================================================
```

### Manual Testing

Test individual components:

```python
# Test agent functionality
from app.crewai.enhanced_agents import enhanced_agent_manager
agents = enhanced_agent_manager.get_all_agents()
print(f"Available agents: {len(agents)}")

# Test task creation
from app.crewai.enhanced_tasks import enhanced_task_manager
tasks = enhanced_task_manager.get_all_tasks()
print(f"Available tasks: {len(tasks)}")

# Test orchestrator validation
from app.crewai.workflow_orchestrator import crewai_orchestrator
valid = await crewai_orchestrator._validate_workflow_structure(workflow_data)
print(f"Workflow valid: {valid['valid']}")
```

## Production Considerations

### Resource Management

- **Rate Limiting**: Configure appropriate RPM limits for your OpenAI usage
- **Timeout Settings**: Adjust timeouts based on workflow complexity
- **Memory Management**: Enable/disable memory based on workflow needs

### Scaling

- **Agent Pool**: Increase agent instances for high-throughput scenarios
- **Parallel Execution**: Enable parallel task execution where possible
- **Load Balancing**: Distribute workloads across multiple worker instances

### Security

- **API Key Management**: Secure storage of OpenAI API keys
- **Input Validation**: Validate all workflow inputs and parameters
- **Output Sanitization**: Clean and validate all agent outputs

### Monitoring

- **Performance Metrics**: Track execution times and success rates
- **Error Tracking**: Monitor and alert on workflow failures
- **Cost Monitoring**: Track OpenAI API usage and costs

## Troubleshooting

### Common Issues

1. **OpenAI API Key Issues**
   ```
   Error: Authentication failed
   Solution: Verify OPENAI_API_KEY is set correctly
   ```

2. **Timeout Errors**
   ```
   Error: Execution timeout
   Solution: Increase CREWAI_MAX_EXECUTION_TIME or simplify workflow
   ```

3. **Memory Issues**
   ```
   Error: Out of memory
   Solution: Reduce CREWAI_MEMORY_LIMIT or disable memory
   ```

4. **Rate Limiting**
   ```
   Error: Rate limit exceeded
   Solution: Reduce CREWAI_MAX_RPM or upgrade OpenAI plan
   ```

### Debug Mode

Enable verbose logging for debugging:

```bash
export CREWAI_VERBOSE_MODE=true
python test-crewai-integration.py
```

### Health Checks

Monitor CrewAI health:

```python
from app.crewai.config import crewai_config
from app.crewai.enhanced_agents import enhanced_agent_manager

# Check configuration
config_health = crewai_config.validate_config()

# Check agents
agents_available = len(enhanced_agent_manager.get_all_agents()) > 0

# Check LLM connectivity
llm_config = crewai_config.get_llm_config()
# ... test LLM connection ...
```

## API Reference

### EnhancedAgentManager

- `get_agent(name: str) -> Agent`: Get specific agent by name
- `get_agents_for_workflow(workflow_type: str) -> List[Agent]`: Get agents for workflow type
- `get_all_agents() -> Dict[str, Agent]`: Get all available agents

### EnhancedTaskManager

- `get_task(name: str) -> Task`: Get specific task by name
- `create_workflow_specific_tasks(workflow_data: Dict) -> List[Task]`: Create workflow tasks
- `get_all_tasks() -> Dict[str, Task]`: Get all available tasks

### CrewAIWorkflowOrchestrator

- `execute_workflow_with_crewai(workflow_data, user_id, execution_id) -> Dict`: Execute workflow
- `_validate_workflow_structure(workflow_data) -> Dict`: Validate workflow structure
- `_create_execution_plan(workflow_data) -> Dict`: Create execution plan

### CrewAIConfig

- `validate_config() -> Dict`: Validate configuration
- `get_llm_config() -> Dict`: Get LLM configuration
- `get_agent_config() -> Dict`: Get agent configuration
- `get_workflow_config() -> Dict`: Get workflow configuration

## Migration Guide

### From Basic CrewAI

1. **Replace imports**:
   ```python
   # Old
   from app.crewai.agents import agent_manager
   from app.crewai.tasks import task_manager
   
   # New
   from app.crewai.enhanced_agents import enhanced_agent_manager
   from app.crewai.enhanced_tasks import enhanced_task_manager
   from app.crewai.workflow_orchestrator import crewai_orchestrator
   ```

2. **Update agent references**:
   ```python
   # Old
   coordinator = agent_manager.get_agent("workflow_coordinator")
   
   # New
   orchestrator = enhanced_agent_manager.get_agent("workflow_orchestrator")
   ```

3. **Use orchestrator for execution**:
   ```python
   # Old: Direct Crew usage
   crew = Crew(agents=agents, tasks=tasks)
   result = crew.kickoff()
   
   # New: Orchestrator usage
   result = await crewai_orchestrator.execute_workflow_with_crewai(workflow_data, user_id, execution_id)
   ```

The CrewAI integration is now complete and provides powerful multi-agent workflow processing capabilities for the Flov7 platform.
