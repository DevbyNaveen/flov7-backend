"""
Condition Executor for Flov7 platform.
Evaluates data and controls workflow branching.
"""

from typing import Dict, Any, Optional, List
import asyncio
import logging
import re
from datetime import datetime

from ..registry import PrimitiveExecutor, PrimitiveExecutionContext

logger = logging.getLogger(__name__)


class ConditionExecutor(PrimitiveExecutor):
    """Executor for condition primitives - evaluates data and controls workflow branching"""
    
    def __init__(self):
        self.supported_conditions = {
            'if_else': self._execute_if_else,
            'filter': self._execute_filter,
            'switch': self._execute_switch,
            'loop': self._execute_loop,
            'compare': self._execute_compare,
            'regex': self._execute_regex,
            'json_path': self._execute_json_path
        }
    
    async def execute(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        condition_type = config.get('condition_type', 'if_else')
        
        if condition_type not in self.supported_conditions:
            raise ValueError(f"Unsupported condition type: {condition_type}")
        
        condition_func = self.supported_conditions[condition_type]
        return await condition_func(config, input_data, context)
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        required_fields = ['condition_type']
        for field in required_fields:
            if field not in config:
                return False, f"Missing required field: {field}"
        
        condition_type = config['condition_type']
        if condition_type not in self.supported_conditions:
            return False, f"Unsupported condition type: {condition_type}"
        
        return True, None
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Data to evaluate against conditions"
                }
            }
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "condition_type": {"type": "string"},
                "result": {"type": "boolean"},
                "branch": {"type": "string"},
                "evaluated_data": {"type": "object"},
                "timestamp": {"type": "string", "format": "date-time"}
            },
            "required": ["condition_type", "result", "timestamp"]
        }
    
    async def _execute_if_else(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        condition = config.get('condition', 'true')
        data = input_data.get('data', {})
        
        # Simple condition evaluation
        result = self._evaluate_condition(condition, data)
        
        return {
            "condition_type": "if_else",
            "result": result,
            "branch": "true" if result else "false",
            "evaluated_data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_filter(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        filter_criteria = config.get('criteria', {})
        data_list = input_data.get('data', [])
        
        if not isinstance(data_list, list):
            data_list = [data_list]
        
        filtered_data = []
        for item in data_list:
            if self._matches_criteria(item, filter_criteria):
                filtered_data.append(item)
        
        return {
            "condition_type": "filter",
            "result": len(filtered_data) > 0,
            "filtered_data": filtered_data,
            "original_count": len(data_list),
            "filtered_count": len(filtered_data),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_switch(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        switch_value = config.get('switch_on', 'value')
        cases = config.get('cases', {})
        data = input_data.get('data', {})
        
        value = data.get(switch_value, 'default')
        matched_case = cases.get(str(value), cases.get('default', 'default'))
        
        return {
            "condition_type": "switch",
            "result": True,
            "switch_value": value,
            "matched_case": matched_case,
            "available_cases": list(cases.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_loop(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        items = input_data.get('data', [])
        if not isinstance(items, list):
            items = [items]
        
        max_iterations = config.get('max_iterations', 100)
        items = items[:max_iterations]
        
        return {
            "condition_type": "loop",
            "result": len(items) > 0,
            "items": items,
            "iteration_count": len(items),
            "max_iterations": max_iterations,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_compare(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        field_a = config.get('field_a', 'value')
        field_b = config.get('field_b', 'compare_to')
        operator = config.get('operator', '==')
        
        data = input_data.get('data', {})
        value_a = data.get(field_a)
        value_b = data.get(field_b)
        
        result = self._apply_comparison(value_a, value_b, operator)
        
        return {
            "condition_type": "compare",
            "result": result,
            "comparison": f"{value_a} {operator} {value_b}",
            "values": {"a": value_a, "b": value_b},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_regex(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        pattern = config.get('pattern', '')
        field = config.get('field', 'text')
        
        data = input_data.get('data', {})
        text = str(data.get(field, ''))
        
        match = re.search(pattern, text)
        
        return {
            "condition_type": "regex",
            "result": match is not None,
            "pattern": pattern,
            "matched_text": match.group() if match else None,
            "full_text": text,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_json_path(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        json_path = config.get('json_path', '$')
        expected_value = config.get('expected_value', None)
        
        data = input_data.get('data', {})
        
        # Simplified JSON path evaluation
        try:
            # Handle simple dot notation for JSON path
            if json_path.startswith('$.'):
                path_parts = json_path[2:].split('.')
                current = data
                for part in path_parts:
                    if isinstance(current, dict):
                        current = current.get(part)
                    else:
                        current = None
                        break
                
                result = current is not None
                if expected_value is not None:
                    result = current == expected_value
                
                return {
                    "condition_type": "json_path",
                    "result": result,
                    "json_path": json_path,
                    "value": current,
                    "expected_value": expected_value,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                # Default behavior
                return {
                    "condition_type": "json_path",
                    "result": True,
                    "json_path": json_path,
                    "fallback": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {
                "condition_type": "json_path",
                "result": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _evaluate_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        """Simple condition evaluation"""
        try:
            # Basic condition evaluation - can be extended
            if condition == 'true':
                return True
            elif condition == 'false':
                return False
            else:
                # Try to evaluate as simple comparison
                return bool(eval(condition, {"__builtins__": {}}, data))
        except:
            return False
    
    def _matches_criteria(self, item: Any, criteria: Dict[str, Any]) -> bool:
        """Check if item matches filter criteria"""
        for key, expected_value in criteria.items():
            if isinstance(item, dict):
                actual_value = item.get(key)
                if actual_value != expected_value:
                    return False
            else:
                return False
        return True
    
    def _apply_comparison(self, value_a: Any, value_b: Any, operator: str) -> bool:
        """Apply comparison operator"""
        try:
            if operator == '==':
                return value_a == value_b
            elif operator == '!=':
                return value_a != value_b
            elif operator == '>':
                return float(value_a) > float(value_b)
            elif operator == '<':
                return float(value_a) < float(value_b)
            elif operator == '>=':
                return float(value_a) >= float(value_b)
            elif operator == '<=':
                return float(value_a) <= float(value_b)
            elif operator == 'contains':
                return str(value_b) in str(value_a)
            else:
                return False
        except (ValueError, TypeError):
            return False
