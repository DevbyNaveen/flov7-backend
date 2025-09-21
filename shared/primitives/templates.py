"""
Primitive Templates for Flov7 platform.
Dynamic template system for generating primitives based on common patterns.
"""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from uuid import uuid4

from shared.constants.primitives import PRIMITIVES


class PrimitiveTemplate:
    """Template for generating primitive configurations"""
    
    def __init__(self, 
                 name: str,
                 description: str,
                 primitive_type: str,
                 subtype: str,
                 config_template: Dict[str, Any],
                 input_schema: Optional[Dict[str, Any]] = None,
                 output_schema: Optional[Dict[str, Any]] = None,
                 tags: Optional[List[str]] = None):
        self.name = name
        self.description = description
        self.primitive_type = primitive_type
        self.subtype = subtype
        self.config_template = config_template
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.tags = tags or []


class PrimitiveTemplateManager:
    """Manager for primitive templates"""
    
    def __init__(self):
        self.templates: Dict[str, PrimitiveTemplate] = {}
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default primitive templates"""
        
        # Trigger Templates
        self.add_template(PrimitiveTemplate(
            name="Webhook Trigger",
            description="Trigger workflow via HTTP webhook",
            primitive_type="trigger",
            subtype="webhook",
            config_template={
                "trigger_type": "webhook",
                "webhook_url": "/webhook",
                "method": "POST",
                "headers": {},
                "authentication": "none"
            },
            tags=["webhook", "http", "trigger"]
        ))
        
        self.add_template(PrimitiveTemplate(
            name="Schedule Trigger",
            description="Trigger workflow on a schedule",
            primitive_type="trigger",
            subtype="schedule",
            config_template={
                "trigger_type": "schedule",
                "schedule": "0 9 * * *",
                "timezone": "UTC",
                "enabled": True
            },
            tags=["schedule", "cron", "time"]
        ))
        
        self.add_template(PrimitiveTemplate(
            name="Manual Trigger",
            description="Trigger workflow manually",
            primitive_type="trigger",
            subtype="manual",
            config_template={
                "trigger_type": "manual",
                "description": "Manually triggered workflow"
            },
            tags=["manual", "user", "trigger"]
        ))
        
        # Action Templates
        self.add_template(PrimitiveTemplate(
            name="Send Email",
            description="Send email notification",
            primitive_type="action",
            subtype="email_send",
            config_template={
                "action_type": "email_send",
                "to_email": "",
                "subject": "Flov7 Workflow Notification",
                "body": "",
                "from_email": "noreply@flov7.com"
            },
            tags=["email", "notification", "communication"]
        ))
        
        self.add_template(PrimitiveTemplate(
            name="API Call",
            description="Make HTTP API request",
            primitive_type="action",
            subtype="api_call",
            config_template={
                "action_type": "api_call",
                "url": "",
                "method": "GET",
                "headers": {},
                "body": {},
                "timeout": 30
            },
            tags=["api", "http", "request"]
        ))
        
        self.add_template(PrimitiveTemplate(
            name="AI Process",
            description="Process data with AI",
            primitive_type="action",
            subtype="ai_process",
            config_template={
                "action_type": "ai_process",
                "prompt": "Process the input data",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            tags=["ai", "processing", "llm"]
        ))
        
        self.add_template(PrimitiveTemplate(
            name="Database Query",
            description="Execute database query",
            primitive_type="action",
            subtype="db_query",
            config_template={
                "action_type": "db_query",
                "query": "SELECT * FROM table",
                "params": {},
                "connection_string": ""
            },
            tags=["database", "sql", "query"]
        ))
        
        # Connection Templates
        self.add_template(PrimitiveTemplate(
            name="Gmail Connection",
            description="Connect to Gmail API",
            primitive_type="connection",
            subtype="gmail",
            config_template={
                "connection_type": "gmail",
                "credentials": {},
                "scopes": ["https://www.googleapis.com/auth/gmail.send"],
                "user_email": ""
            },
            tags=["gmail", "google", "email", "oauth"]
        ))
        
        self.add_template(PrimitiveTemplate(
            name="Slack Connection",
            description="Connect to Slack workspace",
            primitive_type="connection",
            subtype="slack",
            config_template={
                "connection_type": "slack",
                "workspace": "",
                "channels": [],
                "token": ""
            },
            tags=["slack", "messaging", "workspace"]
        ))
        
        self.add_template(PrimitiveTemplate(
            name="Database Connection",
            description="Connect to database",
            primitive_type="connection",
            subtype="database",
            config_template={
                "connection_type": "database",
                "connection_string": "",
                "database_type": "postgresql",
                "pool_size": 10
            },
            tags=["database", "sql", "connection"]
        ))
        
        # Condition Templates
        self.add_template(PrimitiveTemplate(
            name="If-Else Condition",
            description="Branch based on condition",
            primitive_type="condition",
            subtype="if_else",
            config_template={
                "condition_type": "if_else",
                "condition": "data.value > 10",
                "true_branch": "process_high",
                "false_branch": "process_low"
            },
            tags=["condition", "branching", "logic"]
        ))
        
        self.add_template(PrimitiveTemplate(
            name="Data Filter",
            description="Filter data based on criteria",
            primitive_type="condition",
            subtype="filter",
            config_template={
                "condition_type": "filter",
                "criteria": {
                    "status": "active",
                    "priority": "high"
                }
            },
            tags=["filter", "criteria", "selection"]
        ))
        
        self.add_template(PrimitiveTemplate(
            name="Switch Statement",
            description="Multi-way branching",
            primitive_type="condition",
            subtype="switch",
            config_template={
                "condition_type": "switch",
                "switch_on": "type",
                "cases": {
                    "email": "process_email",
                    "sms": "process_sms",
                    "default": "process_other"
                }
            },
            tags=["switch", "multi-branch", "routing"]
        ))
        
        # Data Templates
        self.add_template(PrimitiveTemplate(
            name="Data Mapping",
            description="Map data fields to new structure",
            primitive_type="data",
            subtype="mapping",
            config_template={
                "operation_type": "mapping",
                "mapping_rules": {
                    "old_field": "new_field",
                    "source": "target"
                }
            },
            tags=["mapping", "transformation", "structure"]
        ))
        
        self.add_template(PrimitiveTemplate(
            name="Data Validation",
            description="Validate data against rules",
            primitive_type="data",
            subtype="validate",
            config_template={
                "operation_type": "validate",
                "validation_rules": {
                    "email": {"type": "string", "required": True},
                    "age": {"type": "number", "min": 0, "max": 150}
                }
            },
            tags=["validation", "rules", "quality"]
        ))
        
        self.add_template(PrimitiveTemplate(
            name="Data Enrichment",
            description="Enrich data with additional information",
            primitive_type="data",
            subtype="enrich",
            config_template={
                "operation_type": "enrich",
                "source": "static",
                "enrichment_data": {
                    "processed_at": "{{timestamp}}",
                    "source": "flov7"
                }
            },
            tags=["enrichment", "augmentation", "metadata"]
        ))
    
    def add_template(self, template: PrimitiveTemplate):
        """Add a new template"""
        template_id = f"{template.primitive_type}_{template.subtype}_{uuid4().hex[:8]}"
        self.templates[template_id] = template
        return template_id
    
    def get_template(self, template_id: str) -> Optional[PrimitiveTemplate]:
        """Get a template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self, primitive_type: Optional[str] = None, tags: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """List templates with optional filtering"""
        result = {}
        
        for template_id, template in self.templates.items():
            # Filter by primitive type
            if primitive_type and template.primitive_type != primitive_type:
                continue
            
            # Filter by tags
            if tags and not any(tag in template.tags for tag in tags):
                continue
            
            result[template_id] = {
                "name": template.name,
                "description": template.description,
                "primitive_type": template.primitive_type,
                "subtype": template.subtype,
                "tags": template.tags
            }
        
        return result
    
    def get_templates_by_type(self, primitive_type: str) -> Dict[str, Dict[str, Any]]:
        """Get templates by primitive type"""
        return self.list_templates(primitive_type=primitive_type)
    
    def search_templates(self, query: str) -> Dict[str, Dict[str, Any]]:
        """Search templates by name, description, or tags"""
        query = query.lower()
        result = {}
        
        for template_id, template in self.templates.items():
            if (query in template.name.lower() or
                query in template.description.lower() or
                any(query in tag.lower() for tag in template.tags)):
                
                result[template_id] = {
                    "name": template.name,
                    "description": template.description,
                    "primitive_type": template.primitive_type,
                    "subtype": template.subtype,
                    "tags": template.tags
                }
        
        return result
    
    def generate_primitive_config(self, template_id: str, custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate primitive configuration from template"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        config = template.config_template.copy()
        
        if custom_config:
            # Merge custom configuration
            config.update(custom_config)
        
        # Add template metadata
        config["_template"] = {
            "id": template_id,
            "name": template.name,
            "description": template.description,
            "primitive_type": template.primitive_type,
            "subtype": template.subtype
        }
        
        return config
    
    def create_custom_template(self, 
                              name: str,
                              description: str,
                              primitive_type: str,
                              subtype: str,
                              config_template: Dict[str, Any],
                              tags: Optional[List[str]] = None) -> str:
        """Create a custom template"""
        template = PrimitiveTemplate(
            name=name,
            description=description,
            primitive_type=primitive_type,
            subtype=subtype,
            config_template=config_template,
            tags=tags or []
        )
        
        return self.add_template(template)
    
    def export_templates(self) -> Dict[str, Any]:
        """Export all templates as JSON"""
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "templates": {}
        }
        
        for template_id, template in self.templates.items():
            export_data["templates"][template_id] = {
                "name": template.name,
                "description": template.description,
                "primitive_type": template.primitive_type,
                "subtype": template.subtype,
                "config_template": template.config_template,
                "input_schema": template.input_schema,
                "output_schema": template.output_schema,
                "tags": template.tags
            }
        
        return export_data
    
    def import_templates(self, templates_data: Dict[str, Any]) -> int:
        """Import templates from JSON"""
        imported_count = 0
        
        if "templates" in templates_data:
            for template_id, template_data in templates_data["templates"].items():
                template = PrimitiveTemplate(
                    name=template_data["name"],
                    description=template_data["description"],
                    primitive_type=template_data["primitive_type"],
                    subtype=template_data["subtype"],
                    config_template=template_data["config_template"],
                    input_schema=template_data.get("input_schema"),
                    output_schema=template_data.get("output_schema"),
                    tags=template_data.get("tags", [])
                )
                
                self.templates[template_id] = template
                imported_count += 1
        
        return imported_count


# Global template manager instance
template_manager = PrimitiveTemplateManager()
