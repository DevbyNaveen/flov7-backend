# 5-Primitives System Implementation

## Overview

The 5-Primitives system for Flov7 has been completely implemented with a **runtime registry** and **execution engine**. This system transforms the previously static primitive definitions into a fully functional runtime system capable of executing workflows.

## 🎯 Problem Solved

**Before**: The 5-primitives system was just data structures with constants defined but no runtime functionality.

**After**: Complete runtime system with:
- ✅ **Primitive Registry** - Runtime management and discovery
- ✅ **Primitive Validation Engine** - Runtime configuration validation
- ✅ **Primitive Execution Engine** - Concrete implementations for all 5 primitives
- ✅ **Primitive Template System** - Dynamic generation from templates
- ✅ **Comprehensive Testing** - End-to-end validation

## 🏗️ Architecture

```
shared/primitives/
├── registry.py              # Central registry system
├── templates.py             # Template system for dynamic generation
├── executors/               # Concrete implementations
│   ├── trigger_executor.py  # Trigger primitive execution
│   ├── action_executor.py   # Action primitive execution
│   ├── connection_executor.py # Connection primitive execution
│   ├── condition_executor.py # Condition primitive execution
│   └── data_executor.py     # Data primitive execution
└── __init__.py             # Public API
```

## 🔧 Core Components

### 1. Primitive Registry (`registry.py`)

**Purpose**: Central runtime registry for managing primitive executors

**Key Features**:
- Register/unregister primitive executors
- Execute primitives with validation
- Validate entire workflows
- Manage primitive configurations

**Usage**:
```python
from shared.primitives import primitive_registry

# Execute a primitive
result = await primitive_registry.execute_primitive(
    primitive_type="action",
    config={"action_type": "email_send", "to_email": "user@example.com"},
    input_data={"data": {"message": "Hello World"}},
    context=PrimitiveExecutionContext(execution_id="123", user_id="user123")
)

# Validate workflow
is_valid, error = primitive_registry.validate_workflow_primitives(workflow_data)
```

### 2. Primitive Executors

Each primitive has a dedicated executor with:
- **Runtime configuration validation**
- **Input/output schema validation**
- **Concrete execution logic**
- **Error handling and logging**

#### Trigger Executor
Handles workflow initiation:
- Webhook triggers
- Schedule triggers (cron)
- Database triggers
- Manual triggers
- API triggers
- Email/SMS triggers
- IoT device triggers

#### Action Executor
Performs specific tasks:
- AI processing (LLM integration)
- API calls with HTTP client
- Email sending
- Database queries
- Notifications (Slack, etc.)
- Data transformations
- Custom code execution
- Time delays

#### Connection Executor
Manages external service connections:
- Gmail API integration
- Slack workspace connections
- HubSpot CRM
- Database connections
- OAuth authentication
- API key management
- Webhook endpoints

#### Condition Executor
Evaluates data and controls workflow branching:
- If-else conditions
- Data filtering
- Switch statements
- Loop processing
- Value comparisons
- Regex matching
- JSON path evaluation

#### Data Executor
Manipulates and transforms data:
- Field mapping
- JSON transformations
- Data filtering
- Data merging/splitting
- Data enrichment
- Validation against rules

### 3. Template System (`templates.py`)

**Purpose**: Dynamic primitive generation from templates

**Features**:
- Pre-built templates for common use cases
- Custom template creation
- Template search and filtering
- Import/export functionality

**Available Templates**:
- **Triggers**: Webhook, Schedule, Manual, API, Email, SMS, IoT
- **Actions**: Email, API calls, AI processing, Database queries, Notifications, Transformations
- **Connections**: Gmail, Slack, HubSpot, Database, OAuth, API keys
- **Conditions**: If-else, Filter, Switch, Compare, Regex, JSON path
- **Data**: Mapping, Validation, Enrichment, Transformation

**Usage**:
```python
from shared.primitives import template_manager

# List available templates
templates = template_manager.list_templates(primitive_type="action")

# Generate primitive from template
config = template_manager.generate_primitive_config(
    template_id="action_email_send",
    custom_config={"to_email": "user@example.com"}
)

# Create custom template
template_id = template_manager.create_custom_template(
    name="My Custom Template",
    primitive_type="action",
    subtype="custom",
    config_template={"custom": True}
)
```

## 🚀 Quick Start

### 1. Basic Usage

```python
import asyncio
from shared.primitives import primitive_registry, PrimitiveExecutionContext

async def execute_workflow():
    context = PrimitiveExecutionContext(
        execution_id="workflow-123",
        user_id="user-456"
    )
    
    # 1. Trigger workflow
    trigger_result = await primitive_registry.execute_primitive(
        "trigger",
        {"trigger_type": "manual"},
        {"trigger_data": {"initiated_by": "user-456"}},
        context
    )
    
    # 2. Process data
    data_result = await primitive_registry.execute_primitive(
        "data",
        {"operation_type": "transform", "transform_type": "json"},
        {"data": {"customer": "John Doe", "order": "12345"}},
        context
    )
    
    # 3. Send notification
    action_result = await primitive_registry.execute_primitive(
        "action",
        {
            "action_type": "email_send",
            "to_email": "admin@example.com",
            "subject": "New Order",
            "body": f"New order received: {data_result['data']}"
        },
        {"data": data_result['data']},
        context
    )
    
    return {
        "trigger": trigger_result,
        "data": data_result,
        "action": action_result
    }

# Run the workflow
result = asyncio.run(execute_workflow())
```

### 2. Using Templates

```python
from shared.primitives import template_manager

# Get a template
email_template = template_manager.generate_primitive_config(
    "action_email_send",
    {
        "to_email": "customer@example.com",
        "subject": "Order Confirmation",
        "body": "Your order has been processed successfully."
    }
)

# Use the generated configuration
result = await primitive_registry.execute_primitive(
    "action",
    email_template,
    {"data": {"order_id": "12345"}},
    context
)
```

### 3. Workflow Validation

```python
workflow = {
    "nodes": [
        {
            "type": "trigger",
            "data": {"trigger_type": "webhook", "webhook_url": "/api/webhook"}
        },
        {
            "type": "condition",
            "data": {"condition_type": "if_else", "condition": "data.valid == true"}
        },
        {
            "type": "action",
            "data": {"action_type": "email_send", "to_email": "admin@example.com"}
        }
    ]
}

is_valid, error = primitive_registry.validate_workflow_primitives(workflow)
if is_valid:
    print("Workflow is valid and ready for execution")
else:
    print(f"Workflow validation failed: {error}")
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# From project root
cd flov7-backend
./test-primitives-system.sh
```

## 📊 System Capabilities

### ✅ Runtime Features
- **Dynamic primitive registration**
- **Runtime configuration validation**
- **Input/output schema validation**
- **Error handling and logging**
- **Performance metrics tracking**

### ✅ Primitive Types
1. **Trigger** - 8 different trigger types
2. **Action** - 8 different action types
3. **Connection** - 8 different connection types
4. **Condition** - 7 different condition types
5. **Data** - 7 different data operations

### ✅ Integration Ready
- **Async/await support** for modern Python
- **Type hints** throughout the codebase
- **Comprehensive error handling**
- **Logging integration**
- **Template system** for dynamic generation

## 🔗 Integration with Existing Systems

The primitive system integrates seamlessly with:
- **AI Service** - Can generate primitives from natural language
- **Workflow Service** - Uses primitives for actual workflow execution
- **API Gateway** - Exposes primitive operations via REST API
- **Database** - Stores primitive configurations and execution results

## 🎯 Next Steps

1. **Performance Optimization** - Add caching and connection pooling
2. **Additional Primitive Types** - Expand beyond the 5 core types
3. **Monitoring & Analytics** - Add execution metrics and dashboards
4. **Security Enhancements** - Add authentication and authorization layers
5. **Plugin System** - Allow third-party primitive extensions

## 📚 API Reference

### PrimitiveRegistry
- `execute_primitive(primitive_type, config, input_data, context)`
- `validate_workflow_primitives(workflow_data)`
- `get_primitive_info(primitive_type)`
- `list_executors()`

### TemplateManager
- `generate_primitive_config(template_id, custom_config)`
- `create_custom_template(name, primitive_type, subtype, config_template)`
- `search_templates(query)`
- `export_templates()` / `import_templates(data)`

The 5-primitives system is now **fully functional** and ready for production use!
