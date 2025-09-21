"""
OpenAI client for Flov7 AI service.
Handles communication with OpenAI GPT-4 API for workflow generation.
"""

import openai
import sys
import os
from typing import Optional, Dict, Any, List
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI API client wrapper"""
    
    def __init__(self):
        self.client: Optional[openai.OpenAI] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        if settings.OPENAI_API_KEY:
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            logger.warning("OpenAI API key not configured. AI features will be disabled.")
    
    def generate_workflow(self, prompt: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a workflow based on natural language prompt (basic version)
        
        Args:
            prompt: Natural language description of the workflow
            user_context: Optional user context for personalization
            
        Returns:
            Dict containing the generated workflow and metadata
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Check your API key configuration.")
        
        try:
            # Construct the full prompt with context
            full_prompt = self._construct_workflow_prompt(prompt, user_context)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI workflow generator for Flov7 platform. Generate valid JSON workflow definitions based on user requests."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract and return the generated workflow
            workflow_json_str = response.choices[0].message.content
            workflow_data = self._parse_workflow_response(workflow_json_str)
            
            return {
                "workflow": workflow_data,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model
            }
            
        except Exception as e:
            logger.error(f"Error generating workflow: {str(e)}")
            raise
    
    def generate_workflow_with_system_prompt(self, system_prompt: str, user_prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a workflow using advanced system and user prompts
        
        Args:
            system_prompt: Advanced system prompt for workflow generation
            user_prompt: User's natural language request
            context: Optional context for personalization
            
        Returns:
            Dict containing the generated workflow and metadata
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Check your API key configuration.")
        
        try:
            # Add context to user prompt if provided
            enhanced_user_prompt = user_prompt
            if context:
                enhanced_user_prompt += f"\n\nContext: {context}"
            
            # Call OpenAI API with advanced prompts
            response = self.client.chat.completions.create(
                model=getattr(settings, 'OPENAI_MODEL', 'gpt-4'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enhanced_user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent results
                max_tokens=getattr(settings, 'OPENAI_MAX_TOKENS', 4000)
            )
            
            # Extract and return the generated workflow
            workflow_json_str = response.choices[0].message.content
            workflow_data = self._parse_workflow_response(workflow_json_str)
            
            return {
                "workflow": workflow_data,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "advanced_prompts": True
            }
            
        except Exception as e:
            logger.error(f"Error generating workflow with advanced prompts: {str(e)}")
            raise
    
    def _construct_workflow_prompt(self, prompt: str, user_context: Optional[Dict[str, Any]] = None) -> str:
        """Construct the full prompt for workflow generation"""
        base_prompt = f"""
You are an expert workflow automation engineer. Generate a workflow definition in JSON format based on the following request:
"{prompt}"

IMPORTANT: Use ONLY the 5 Flov7 primitives system:
1. TRIGGER - Starts workflows (webhook, schedule, database, manual, api, email, sms, iot)
2. ACTION - Performs tasks (ai_process, api_call, email_send, db_query, notification, transform, wait, custom)
3. CONNECTION - Connects to services (gmail, slack, hubspot, database, api, webhook, oauth, api_key)
4. CONDITION - Controls flow (if_else, filter, switch, loop, compare, regex, json_path)
5. DATA - Handles data (mapping, transform, filter, merge, split, enrich, validate)

Required JSON structure:
{{
  "name": "descriptive workflow name",
  "description": "clear description of what this workflow does",
  "nodes": [
    {{
      "id": "unique_node_id",
      "type": "trigger|action|connection|condition|data",
      "position": {{"x": 100, "y": 100}},
      "data": {{
        "label": "Node Label",
        "config": {{
          // Node-specific configuration
        }}
      }}
    }}
  ],
  "edges": [
    {{
      "id": "edge_id",
      "source": "source_node_id",
      "target": "target_node_id",
      "sourceHandle": "output",
      "targetHandle": "input"
    }}
  ]
}}

RULES:
- Start with a trigger node (webhook, schedule, etc.)
- Connect nodes logically with edges
- Use realistic x,y positions (increment by 200-300)
- Include proper configuration in data.config
- Make the workflow actually functional
- Return ONLY valid JSON, no markdown or extra text

Example for "Send welcome email when user signs up":
{{
  "name": "Welcome Email Workflow",
  "description": "Sends a welcome email when a new user signs up",
  "nodes": [
    {{
      "id": "trigger_1",
      "type": "trigger",
      "position": {{"x": 100, "y": 100}},
      "data": {{
        "label": "User Signup Webhook",
        "config": {{
          "trigger_type": "webhook",
          "endpoint": "/webhook/user-signup",
          "method": "POST"
        }}
      }}
    }},
    {{
      "id": "action_1",
      "type": "action",
      "position": {{"x": 400, "y": 100}},
      "data": {{
        "label": "Send Welcome Email",
        "config": {{
          "action_type": "email_send",
          "template": "welcome_email",
          "to": "{{{{user.email}}}}",
          "subject": "Welcome to our platform!"
        }}
      }}
    }}
  ],
  "edges": [
    {{
      "id": "edge_1",
      "source": "trigger_1",
      "target": "action_1",
      "sourceHandle": "output",
      "targetHandle": "input"
    }}
  ]
}}
"""
        
        if user_context:
            base_prompt += f"\n\nUser context: {user_context}"
        
        return base_prompt
    
    def _parse_workflow_response(self, response_str: str) -> Dict[str, Any]:
        """Parse the workflow response from OpenAI"""
        import json
        import re
        
        # Extract JSON from response (in case there's extra text)
        json_match = re.search(r'\{.*\}', response_str, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # If extraction failed, try parsing the whole response
        try:
            return json.loads(response_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse workflow JSON: {str(e)}")


# Global OpenAI client instance
openai_client = OpenAIClient()
