# AI Service Integration - API Gateway to AI Service

This document describes the integration between the API Gateway and AI Service for workflow generation.

## Overview

The API Gateway now includes a new endpoint `/api/v1/workflows/generate` that allows users to create workflows from natural language prompts using AI-powered generation.

## New Features

### 🚀 Workflow Generation Endpoint

**Endpoint:** `POST /api/v1/workflows/generate`

**Description:** Generates a complete workflow from a natural language prompt using the AI service.

**Authentication:** Required (JWT Bearer token)

### Request Format

```json
{
  "prompt": "Create a workflow that processes customer support tickets",
  "name": "Support Ticket Processor",
  "description": "Automatically processes and routes support tickets",
  "tags": ["support", "automation", "routing"]
}
```

**Required Fields:**
- `prompt` (string): Natural language description of the desired workflow

**Optional Fields:**
- `name` (string): Custom name for the generated workflow (auto-generated if not provided)
- `description` (string): Custom description (auto-generated from prompt if not provided)
- `tags` (array): List of tags to associate with the workflow

### Response Format

```json
{
  "success": true,
  "workflow": {
    "name": "Support Ticket Processor",
    "primitives": [...],
    "connections": [...],
    "metadata": {...}
  },
  "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
  "ai_metadata": {
    "model_used": "gpt-4",
    "prompt_tokens": 150,
    "completion_tokens": 450,
    "processing_time": 2.3
  },
  "message": "Workflow generated successfully using AI"
}
```

## Error Handling

The endpoint includes comprehensive error handling:

- **400 Bad Request**: Invalid prompt or request format
- **401 Unauthorized**: Missing or invalid authentication
- **429 Too Many Requests**: AI service rate limit exceeded
- **502 Bad Gateway**: AI service returned an error
- **503 Service Unavailable**: AI service is not accessible

## Architecture

### Service Communication

```
API Gateway → AI Service → Database → API Gateway
     ↓           ↓          ↓         ↓
  Validate   Generate    Persist   Return
  Request    Workflow    Workflow  Response
```

### Configuration

**Environment Variables:**
- `AI_SERVICE_HOST`: AI service hostname (default: 0.0.0.0)
- `AI_SERVICE_PORT`: AI service port (default: 8001)
- `API_GATEWAY_PORT`: API Gateway port (default: 8000)

## Testing

### Quick Test

1. **Start services:**
   ```bash
   docker-compose up -d
   ```

2. **Get authentication token:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"testpassword"}'
   ```

3. **Generate workflow:**
   ```bash
   export TOKEN="your-jwt-token-here"
   
   curl -X POST http://localhost:8000/api/v1/workflows/generate \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Create a workflow that processes customer support tickets",
       "name": "Support Ticket Processor",
       "description": "Automatically processes and routes support tickets",
       "tags": ["support", "automation", "routing"]
     }'
   ```

### Test Scripts

- `test_workflow_generation.py`: Python test script with examples
- `test_workflow_generation_curl.sh`: cURL-based test script

### Example Prompts

**Data Processing:**
- "Create a workflow that extracts data from CSV files and generates email reports"
- "Build a pipeline that processes sales data and creates monthly summaries"

**Automation:**
- "Create an automation that sends welcome emails to new users"
- "Build a workflow that monitors website uptime and sends alerts"

**Business Logic:**
- "Create a workflow that approves expense reports based on amount thresholds"
- "Build a system that categorizes support tickets and assigns them to teams"

## API Documentation

### Health Check

The workflows endpoint health check now includes AI generation capability:

```bash
curl http://localhost:8000/api/v1/workflows/health
```

Response:
```json
{
  "status": "healthy",
  "service": "workflows",
  "features": [
    "crud_operations",
    "execution_tracking",
    "template_support",
    "pagination",
    "filtering",
    "ai_generation"
  ]
}
```

## Development

### Adding New Features

1. **Extend Pydantic models** in `workflows.py` if needed
2. **Update error handling** for new edge cases
3. **Add tests** for new functionality
4. **Update documentation** for API changes

### Dependencies

New dependencies added:
- `httpx`: HTTP client for service communication
- Enhanced error handling for service-to-service calls

## Troubleshooting

### Common Issues

1. **AI Service Unreachable**
   - Check if AI service is running on port 8001
   - Verify `AI_SERVICE_HOST` and `AI_SERVICE_PORT` environment variables

2. **Authentication Errors**
   - Ensure valid JWT token is provided
   - Check token expiration

3. **Rate Limiting**
   - AI service has rate limiting (10 requests/minute)
   - Implement exponential backoff in client applications

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
export DEBUG=true
```

### Service Logs

Check service logs:
```bash
docker-compose logs api-gateway
docker-compose logs ai-service
```

## Security Considerations

- All requests require authentication
- Rate limiting is enforced at the AI service level
- Input validation is performed on both API Gateway and AI service
- Sensitive data is not logged

## Future Enhancements

- **Custom AI Models**: Allow users to specify AI model preferences
- **Template Integration**: Generate workflows from templates with AI customization
- **Batch Generation**: Generate multiple workflows from a single prompt
- **Version History**: Track AI generation history for workflows
- **Performance Metrics**: Detailed analytics on generation performance
