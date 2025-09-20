"""
OpenAI client for Flov7 AI service.
Handles communication with OpenAI GPT-4 API for workflow generation.
"""

import openai
from shared.config.settings import settings
from typing import Optional, Dict, Any, List
import logging

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
        Generate a workflow based on natural language prompt
        
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
    
    def _construct_workflow_prompt(self, prompt: str, user_context: Optional[Dict[str, Any]] = None) -> str:
        """Construct the full prompt for workflow generation"""
        base_prompt = f"""
Generate a workflow definition in JSON format based on the following request:
"{prompt}"

The workflow should follow this structure:
- name: string (workflow name)
- description: string (workflow description)
- nodes: array of node objects with id, type, position, data
- edges: array of edge objects with id, source, target, sourceHandle, targetHandle

Each node should have:
- id: unique identifier
- type: one of the 5 primitives (trigger, action, connection, condition, data)
- position: object with x, y coordinates
- data: object with configuration data

Return only the JSON workflow definition without any additional text or formatting.
"""
        
        if user_context:
            base_prompt += f"\nUser context: {user_context}"
        
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
