# Temporal Integration Guide - Flov7 Workflow Service

## Overview

This guide provides comprehensive instructions for setting up and using the Temporal integration in the Flov7 workflow service. The integration provides robust workflow orchestration, execution, and monitoring capabilities.

## Architecture

### Components

1. **Temporal Client** (`app/temporal/client.py`) - Manages connection to Temporal server
2. **Activities** (`app/temporal/activities.py`) - Defines workflow node execution logic
3. **Workflows** (`app/temporal/workflows.py`) - Orchestrates workflow execution
4. **Worker** (`app/temporal/worker.py`) - Processes workflows and activities
5. **Configuration** (`app/temporal/config.py`) - Centralized Temporal settings

### Workflow Types

- **WorkflowExecution**: Executes complete workflows with dependency resolution
- **WorkflowValidation**: Validates workflow structure and dependencies

## Setup Instructions

### 1. Temporal Server Setup

#### Option A: Local Development (Docker)
```bash
# Start Temporal server with development setup
docker run -d --name temporal-dev-server \
  -p 7233:7233 \
  -p 8233:8233 \
  temporalio/server:latest \
  --dynamic-config-value system.forceSearchAttributesCacheRefreshOnRead=false
```

#### Option B: Production Setup
- Install Temporal server cluster
- Configure persistence layer (PostgreSQL/MySQL)
- Set up Elasticsearch for advanced visibility
- Configure TLS/SSL certificates

### 2. Environment Configuration

Create `.env` file in workflow-service directory:

```bash
# Temporal Configuration
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=flov7-workflow-task-queue

# Worker Configuration
START_TEMPORAL_WORKER=true
TEMPORAL_MAX_CONCURRENT_WORKFLOWS=10
TEMPORAL_MAX_CONCURRENT_ACTIVITIES=5

# Timeout Configuration
TEMPORAL_WORKFLOW_TIMEOUT_MINUTES=30
TEMPORAL_ACTIVITY_TIMEOUT_MINUTES=5
TEMPORAL_NODE_TIMEOUT_MINUTES=5

# Retry Configuration
TEMPORAL_WORKFLOW_MAX_RETRIES=3
TEMPORAL_ACTIVITY_MAX_RETRIES=3
TEMPORAL_WORKFLOW_INITIAL_INTERVAL_SECONDS=1
TEMPORAL_WORKFLOW_BACKOFF_COEFFICIENT=2.0
```

### 3. Running the Temporal Worker

#### Option A: Integrated with FastAPI
```bash
# Start with worker enabled
START_TEMPORAL_WORKER=true uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

#### Option B: Separate Worker Process
```bash
# Run dedicated worker
python temporal-worker.py

# Or with environment variables
TEMPORAL_HOST=localhost:7233 python temporal-worker.py
```

#### Option C: Docker Compose
```yaml
# Add to docker-compose.yml
version: '3.8'
services:
  workflow-service:
    build: .
    ports:
      - "8002:8002"
    environment:
      - TEMPORAL_HOST=temporal:7233
      - START_TEMPORAL_WORKER=true
    depends_on:
      - temporal
      - redis
      - postgres

  temporal-worker:
    build: .
    command: python temporal-worker.py
    environment:
      - TEMPORAL_HOST=temporal:7233
    depends_on:
      - temporal
      - redis
      - postgres

  temporal:
    image: temporalio/server:latest
    ports:
      - "7233:7233"
      - "8233:8233"
```

## Usage Examples

### 1. Executing a Workflow

```python
import asyncio
from app.temporal.client import get_temporal_client
from app.temporal.workflows import WorkflowExecution

async def execute_workflow_example():
    # Get Temporal client
    client = await get_temporal_client()
    
    # Workflow definition
    workflow_data = {
        "id": "test-workflow-001",
        "name": "Test Workflow",
        "nodes": [
            {
                "id": "node-1",
                "type": "api_call",
                "data": {
                    "url": "https://api.example.com/data",
                    "method": "GET"
                }
            },
            {
                "id": "node-2", 
                "type": "transform",
                "data": {
                    "transform_type": "mapping",
                    "mapping": {
                        "result": "inputs.data"
                    }
                }
            }
        ],
        "edges": [
            {"id": "edge-1", "source": "node-1", "target": "node-2"}
        ]
    }
    
    # Execute workflow
    handle = await client.start_workflow(
        WorkflowExecution.run,
        workflow_data,
        id="test-execution-001",
        task_queue="flov7-workflow-task-queue"
    )
    
    # Wait for result
    result = await handle.result()
    print(f"Workflow result: {result}")
```

### 2. Validating a Workflow

```python
from app.temporal.workflows import WorkflowValidation

async def validate_workflow_example():
    client = await get_temporal_client()
    
    validation_result = await client.execute_workflow(
        WorkflowValidation.run,
        workflow_data,
        id="validation-001",
        task_queue="flov7-workflow-task-queue"
    )
    
    if validation_result["valid"]:
        print("Workflow is valid")
    else:
        print(f"Validation issues: {validation_result['issues']}")
```

### 3. Monitoring Workflow Status

```python
async def monitor_workflow(execution_id: str):
    client = await get_temporal_client()
    
    handle = client.get_workflow_handle(execution_id)
    
    # Query workflow status
    status = await handle.query("get_status")
    print(f"Workflow status: {status}")
    
    # Cancel workflow if needed
    await handle.signal("cancel_workflow")
```

## Node Types and Activities

### Supported Node Types

1. **api_call**: Makes HTTP API requests
   - Configuration: `url`, `method`, `headers`, `body`
   - Input: Request parameters
   - Output: Response data

2. **condition**: Evaluates conditional logic
   - Configuration: `condition` (Python expression)
   - Input: Variables for evaluation
   - Output: Boolean result

3. **transform**: Transforms data
   - Configuration: `transform_type`, `mapping`
   - Input: Source data
   - Output: Transformed data

4. **delay**: Adds delays
   - Configuration: `delay_seconds`
   - Input: None
   - Output: Delay confirmation

5. **database**: Database operations
   - Configuration: `operation`, `table`, `query`
   - Input: Operation parameters
   - Output: Query results

6. **webhook**: Sends webhooks
   - Configuration: `url`, `method`, `payload`
   - Input: Data to send
   - Output: Delivery status

7. **ai_agent**: AI processing
   - Configuration: `agent_type`, `prompt`
   - Input: Data to process
   - Output: AI response

## Error Handling and Retry Policies

### Workflow Retry Policy
- **Maximum attempts**: 3
- **Initial interval**: 1 second
- **Maximum interval**: 10 seconds
- **Backoff coefficient**: 2.0

### Activity Retry Policy
- **Maximum attempts**: 3
- **Initial interval**: 1 second
- **Maximum interval**: 10 seconds
- **Backoff coefficient**: 2.0

### Node Execution
- **Timeout**: 5 minutes per node
- **Retry**: 3 attempts with exponential backoff
- **Error handling**: Detailed error messages and logging

## Monitoring and Observability

### Logging
- Structured logging with correlation IDs
- Activity execution logs
- Workflow lifecycle events
- Error tracking and debugging

### Metrics (Optional)
- Worker metrics via Prometheus
- Workflow execution counts
- Activity success/failure rates
- Performance metrics

### Health Checks
- Temporal server connectivity
- Worker status
- Task queue health

## Testing

### 1. Unit Tests
```bash
# Run Temporal-specific tests
python -m pytest tests/test_temporal/ -v
```

### 2. Integration Tests
```bash
# Test with Temporal server
python test-temporal-integration.py
```

### 3. Load Testing
```bash
# Run load tests
python test-temporal-load.py --workflows 100 --concurrent 10
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   ```
   Error: Failed to connect to Temporal server
   Solution: Check TEMPORAL_HOST and ensure server is running
   ```

2. **Task Queue Not Found**
   ```
   Error: Task queue not found
   Solution: Ensure worker is running with correct task queue name
   ```

3. **Workflow Timeout**
   ```
   Error: Workflow execution timeout
   Solution: Increase TEMPORAL_WORKFLOW_TIMEOUT_MINUTES
   ```

4. **Activity Failure**
   ```
   Error: Activity execution failed
   Solution: Check activity logs and retry configuration
   ```

### Debug Mode
```bash
# Enable debug logging
TEMPORAL_DEBUG=true python temporal-worker.py
```

### Health Check Endpoint
```bash
# Check worker health
curl http://localhost:8002/health/temporal
```

## Production Considerations

### Security
- Use TLS/SSL certificates
- Implement proper authentication
- Secure Temporal server configuration
- Network isolation

### Scalability
- Run multiple worker instances
- Use task queue partitioning
- Implement proper resource limits
- Monitor worker performance

### High Availability
- Temporal server clustering
- Worker redundancy
- Database replication
- Health monitoring

### Configuration Management
- Environment-specific configs
- Secrets management
- Configuration validation
- Deployment automation

## API Integration

The Temporal integration works seamlessly with the existing API endpoints:

- `POST /api/v1/workflow/execute/` - Uses Temporal orchestration
- `GET /api/v1/workflow/status/{execution_id}` - Monitors Temporal workflows
- `GET /api/v1/workflow/history/{execution_id}` - Views execution history

## Migration from Local Execution

### Steps to Migrate
1. Deploy Temporal server
2. Update environment configuration
3. Start Temporal worker
4. Test with existing workflows
5. Monitor performance
6. Gradually migrate production workloads

### Backward Compatibility
- Local execution fallback available
- Configurable via ENABLE_TEMPORAL_FEATURES
- Gradual migration support
