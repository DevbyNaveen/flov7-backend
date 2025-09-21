# AI Service to Workflow Service Integration Guide

This document describes the complete integration between the AI Service and Workflow Service, enabling AI-generated workflows to be executed automatically.

## Overview

The integration provides seamless communication between:
- **AI Service** (Port 8001): Generates workflows from natural language prompts
- **Workflow Service** (Port 8002): Executes workflows using Temporal and CrewAI

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User/API      │    │   AI Service     │    │ Workflow Service│
│                 │───▶│  (Port 8001)    │───▶│  (Port 8002)   │
│                 │    │                 │    │                 │
│                 │◄───│                 │◄───│                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## New Endpoints Added

### AI Service Endpoints

#### 1. Execute Existing Workflow
```http
POST /ai/workflows/{workflow_id}/execute
Content-Type: application/json

{
  "user_id": "user123"
}
```

**Response:**
```json
{
  "execution_id": "exec_123456",
  "status": "running",
  "workflow_id": "wf_789012",
  "user_id": "user123",
  "message": "Workflow execution started successfully"
}
```

#### 2. Check Execution Status
```http
GET /ai/workflows/execution/{execution_id}/status?user_id=user123
```

**Response:**
```json
{
  "execution_id": "exec_123456",
  "status": "completed",
  "workflow_id": "wf_789012",
  "user_id": "user123",
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:45Z",
  "execution_time_seconds": 45.0,
  "output_data": {
    "result": "Workflow executed successfully"
  },
  "error_message": null
}
```

#### 3. Generate and Execute in One Call
```http
POST /ai/workflows/generate-and-execute
Content-Type: application/json

{
  "prompt": "Create a workflow that processes customer support tickets",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "workflow": {
    "name": "Customer Support Ticket Processor",
    "nodes": [...],
    "edges": [...]
  },
  "ai_metadata": {
    "workflow_id": "wf_789012",
    "prompt": "Create a workflow that processes customer support tickets",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "execution": {
    "execution_id": "exec_123456",
    "status": "running",
    "message": "Workflow generated and execution started successfully"
  }
}
```

### Workflow Service Endpoints (Enhanced)

The Workflow Service endpoints have been enhanced to include `workflow_id` in responses:

#### Execute Workflow
```http
POST /workflow/execute
Content-Type: application/json

{
  "workflow_data": {
    "id": "wf_789012",
    "name": "Customer Support Processor",
    "nodes": [...],
    "edges": [...]
  },
  "user_id": "user123"
}
```

**Enhanced Response:**
```json
{
  "execution_id": "exec_123456",
  "status": "running",
  "workflow_id": "wf_789012",
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": null,
  "execution_time_seconds": null
}
```

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# AI Service Configuration
WORKFLOW_SERVICE_URL=http://localhost:8002
WORKFLOW_SERVICE_TIMEOUT=30
ENABLE_WORKFLOW_EXECUTION=true

# Workflow Service Configuration (already exists)
WORKFLOW_SERVICE_HOST=0.0.0.0
WORKFLOW_SERVICE_PORT=8002
```

### Service Dependencies

The integration requires:
- **httpx**: HTTP client for service communication (already in requirements)
- **FastAPI**: Web framework (already in requirements)
- **Pydantic**: Data validation (already in requirements)

## Usage Examples

### 1. Basic Workflow Generation and Execution

```bash
# Step 1: Generate a workflow
curl -X POST http://localhost:8001/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a workflow that automatically responds to customer emails",
    "user_id": "user123"
  }'

# Step 2: Execute the generated workflow
curl -X POST http://localhost:8001/ai/workflows/{workflow_id}/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123"
  }'

# Step 3: Check execution status
curl "http://localhost:8001/ai/workflows/execution/{execution_id}/status?user_id=user123"
```

### 2. One-Step Generation and Execution

```bash
# Generate and execute in a single call
curl -X POST http://localhost:8001/ai/workflows/generate-and-execute \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a workflow that monitors social media mentions and sends alerts",
    "user_id": "user123"
  }'
```

### 3. Python Client Example

```python
import httpx
import asyncio

async def generate_and_execute_workflow(prompt: str, user_id: str):
    async with httpx.AsyncClient() as client:
        # Generate workflow
        response = await client.post(
            "http://localhost:8001/ai/generate",
            json={"prompt": prompt, "user_id": user_id}
        )
        workflow_data = response.json()
        
        # Execute workflow
        response = await client.post(
            f"http://localhost:8001/ai/workflows/{workflow_data['ai_metadata']['workflow_id']}/execute",
            json={"user_id": user_id}
        )
        
        return response.json()

# Usage
result = asyncio.run(generate_and_execute_workflow(
    "Create a workflow that processes new user registrations",
    "user123"
))
print(f"Execution ID: {result['execution_id']}")
```

## Error Handling

### Common Error Responses

#### Service Unavailable
```json
{
  "detail": "Workflow Service unavailable"
}
```

#### Workflow Not Found
```json
{
  "detail": "Workflow not found"
}
```

#### Invalid Request
```json
{
  "detail": "Invalid workflow ID format"
}
```

#### Rate Limit Exceeded
```json
{
  "detail": "Rate limit exceeded"
}
```

### Retry Logic

The integration includes automatic retry logic for:
- Network timeouts (30s default)
- Service unavailability (with exponential backoff)
- Rate limiting (respects retry-after headers)

## Testing

### Automated Testing

Run the integration test script:

```bash
# Make the script executable
chmod +x test-ai-workflow-integration.sh

# Run the tests
./test-ai-workflow-integration.sh
```

### Manual Testing

Test each endpoint individually:

```bash
# Test 1: Health checks
curl http://localhost:8001/health
curl http://localhost:8002/health

# Test 2: Generate workflow
curl -X POST http://localhost:8001/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test workflow", "user_id": "test"}'

# Test 3: Execute workflow directly
curl -X POST http://localhost:8002/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{"workflow_data": {"name": "Test", "nodes": []}, "user_id": "test"}'
```

## Monitoring

### Health Check Endpoints

- **AI Service**: `http://localhost:8001/health`
- **Workflow Service**: `http://localhost:8002/health`

### Logging

The integration provides detailed logging:
- **AI Service**: Logs all workflow execution requests and responses
- **Workflow Service**: Logs execution status updates and errors

### Metrics

Available metrics include:
- Workflow generation count
- Workflow execution count
- Execution success/failure rates
- Average execution time
- Service response times

## Troubleshooting

### Common Issues

1. **Service Connection Failed**
   - Check if both services are running
   - Verify network connectivity between services
   - Check firewall settings

2. **Workflow Execution Timeout**
   - Increase `WORKFLOW_SERVICE_TIMEOUT` in environment
   - Check Temporal service status
   - Review workflow complexity

3. **Rate Limiting**
   - Implement backoff strategy in client
   - Monitor rate limit headers
   - Consider batch processing for multiple workflows

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python -m app.main
```

## Security Considerations

- All endpoints require user_id for authorization
- Rate limiting is implemented on all endpoints
- Input validation is performed on all requests
- Service-to-service communication uses internal networks only

## Future Enhancements

- WebSocket support for real-time execution updates
- Batch workflow execution
- Advanced workflow scheduling
- Integration with external workflow engines
- Workflow execution analytics dashboard
