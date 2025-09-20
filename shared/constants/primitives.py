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
        "color": "#4CAF50"
    },
    "action": {
        "name": "action",
        "display_name": "Action",
        "description": "Performs a specific task or operation",
        "icon": "bolt",
        "color": "#2196F3"
    },
    "connection": {
        "name": "connection",
        "display_name": "Connection",
        "description": "Connects to external services and APIs",
        "icon": "link",
        "color": "#9C27B0"
    },
    "condition": {
        "name": "condition",
        "display_name": "Condition",
        "description": "Evaluates data and controls workflow branching",
        "icon": "fork_right",
        "color": "#FF9800"
    },
    "data": {
        "name": "data",
        "display_name": "Data",
        "description": "Manipulates, transforms, or stores data",
        "icon": "data_object",
        "color": "#F44336"
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
