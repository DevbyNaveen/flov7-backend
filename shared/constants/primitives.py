"""
Primitive constants for Flov7 platform.
Defines the 5-primitives system and related constants.
"""

# The 5 Primitives of Flov7 Workflow Automation
PRIMITIVES = {
    "trigger": {
        "name": "trigger",
        "display_name": "Trigger",
        "description": "Starts the workflow execution based on an event or schedule",
        "icon": "play_arrow",
        "color": "#4CAF50",
        "subtypes": {
            "webhook": {"name": "Webhook", "description": "HTTP webhook trigger"},
            "schedule": {"name": "Schedule", "description": "Time-based trigger"},
            "database": {"name": "Database", "description": "Database change trigger"},
            "manual": {"name": "Manual", "description": "Manual execution trigger"},
            "api": {"name": "API", "description": "API endpoint trigger"},
            "email": {"name": "Email", "description": "Email received trigger"},
            "sms": {"name": "SMS", "description": "SMS received trigger"},
            "iot": {"name": "IoT", "description": "IoT device trigger"}
        }
    },
    "action": {
        "name": "action",
        "display_name": "Action",
        "description": "Performs a specific task or operation",
        "icon": "bolt",
        "color": "#2196F3",
        "subtypes": {
            "ai_process": {"name": "AI Process", "description": "AI-powered processing"},
            "api_call": {"name": "API Call", "description": "HTTP API request"},
            "email_send": {"name": "Send Email", "description": "Send email message"},
            "db_query": {"name": "Database Query", "description": "Execute database query"},
            "notification": {"name": "Notification", "description": "Send notification"},
            "transform": {"name": "Transform", "description": "Transform data"},
            "wait": {"name": "Wait", "description": "Wait/delay execution"},
            "custom": {"name": "Custom", "description": "Custom action"}
        }
    },
    "connection": {
        "name": "connection",
        "display_name": "Connection",
        "description": "Connects to external services and APIs",
        "icon": "link",
        "color": "#9C27B0",
        "subtypes": {
            "gmail": {"name": "Gmail", "description": "Gmail connection"},
            "slack": {"name": "Slack", "description": "Slack connection"},
            "hubspot": {"name": "HubSpot", "description": "HubSpot CRM connection"},
            "database": {"name": "Database", "description": "Database connection"},
            "api": {"name": "API", "description": "Generic API connection"},
            "webhook": {"name": "Webhook", "description": "Webhook connection"},
            "oauth": {"name": "OAuth", "description": "OAuth authentication"},
            "api_key": {"name": "API Key", "description": "API key authentication"}
        }
    },
    "condition": {
        "name": "condition",
        "display_name": "Condition",
        "description": "Evaluates data and controls workflow branching",
        "icon": "fork_right",
        "color": "#FF9800",
        "subtypes": {
            "if_else": {"name": "If/Else", "description": "Conditional branching"},
            "filter": {"name": "Filter", "description": "Filter data"},
            "switch": {"name": "Switch", "description": "Multi-way branching"},
            "loop": {"name": "Loop", "description": "Iterate over data"},
            "compare": {"name": "Compare", "description": "Compare values"},
            "regex": {"name": "Regex", "description": "Regular expression matching"},
            "json_path": {"name": "JSON Path", "description": "JSON path evaluation"}
        }
    },
    "data": {
        "name": "data",
        "display_name": "Data",
        "description": "Manipulates, transforms, or stores data",
        "icon": "data_object",
        "color": "#F44336",
        "subtypes": {
            "mapping": {"name": "Mapping", "description": "Map data fields"},
            "transform": {"name": "Transform", "description": "Transform data structure"},
            "filter": {"name": "Filter", "description": "Filter data"},
            "merge": {"name": "Merge", "description": "Merge data sources"},
            "split": {"name": "Split", "description": "Split data"},
            "enrich": {"name": "Enrich", "description": "Enrich with external data"},
            "validate": {"name": "Validate", "description": "Validate data"}
        }
    }
}

# Common primitive categories
PRIMITIVE_CATEGORIES = [
    "communication",
    "data_processing",
    "file_operations",
    "database",
    "webhooks",
    "scheduling",
    "ai_operations",
    "utilities"
]

# Default primitive configuration schema
DEFAULT_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Name of the primitive instance"
        },
        "description": {
            "type": "string",
            "description": "Description of what this primitive does"
        }
    },
    "required": ["name"]
}

# Default primitive input schema
DEFAULT_INPUT_SCHEMA = {
    "type": "object",
    "properties": {},
    "additionalProperties": True
}

# Default primitive output schema
DEFAULT_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {},
    "additionalProperties": True
}
