"""
Data Executor for Flov7 platform.
Manipulates, transforms, and manages data operations.
"""

from typing import Dict, Any, Optional, List
import asyncio
import logging
import json
from datetime import datetime

from ..registry import PrimitiveExecutor, PrimitiveExecutionContext

logger = logging.getLogger(__name__)


class DataExecutor(PrimitiveExecutor):
    """Executor for data primitives - manipulates and transforms data"""
    
    def __init__(self):
        self.supported_operations = {
            'mapping': self._execute_mapping,
            'transform': self._execute_transform,
            'filter': self._execute_filter,
            'merge': self._execute_merge,
            'split': self._execute_split,
            'enrich': self._execute_enrich,
            'validate': self._execute_validate
        }
    
    async def execute(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        operation_type = config.get('operation_type', 'transform')
        
        if operation_type not in self.supported_operations:
            raise ValueError(f"Unsupported data operation: {operation_type}")
        
        operation_func = self.supported_operations[operation_type]
        return await operation_func(config, input_data, context)
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        required_fields = ['operation_type']
        for field in required_fields:
            if field not in config:
                return False, f"Missing required field: {field}"
        
        operation_type = config['operation_type']
        if operation_type not in self.supported_operations:
            return False, f"Unsupported data operation: {operation_type}"
        
        return True, None
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": ["object", "array", "string", "number", "boolean"],
                    "description": "Input data to process"
                }
            }
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation_type": {"type": "string"},
                "result": {"type": "object"},
                "success": {"type": "boolean"},
                "metadata": {"type": "object"},
                "timestamp": {"type": "string", "format": "date-time"}
            },
            "required": ["operation_type", "success", "timestamp"]
        }
    
    async def _execute_mapping(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        mapping_rules = config.get('mapping_rules', {})
        data = input_data.get('data', {})
        
        if not isinstance(data, dict):
            return {
                "operation_type": "mapping",
                "result": {},
                "success": False,
                "error": "Input data must be a dictionary for mapping",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        mapped_data = {}
        for source_key, target_key in mapping_rules.items():
            if source_key in data:
                mapped_data[target_key] = data[source_key]
        
        return {
            "operation_type": "mapping",
            "result": mapped_data,
            "success": True,
            "metadata": {
                "source_keys": list(data.keys()),
                "mapped_keys": list(mapped_data.keys()),
                "rules_applied": len(mapping_rules)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_transform(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        transform_type = config.get('transform_type', 'json')
        data = input_data.get('data', {})
        
        transformed_data = data
        
        if transform_type == 'json':
            # JSON transformation
            if isinstance(data, str):
                try:
                    transformed_data = json.loads(data)
                except json.JSONDecodeError:
                    transformed_data = {"error": "Invalid JSON string"}
            else:
                transformed_data = json.dumps(data) if not isinstance(data, str) else data
        
        elif transform_type == 'flatten':
            # Flatten nested structure
            transformed_data = self._flatten_dict(data) if isinstance(data, dict) else data
        
        elif transform_type == 'normalize':
            # Normalize data structure
            transformed_data = self._normalize_data(data)
        
        return {
            "operation_type": "transform",
            "result": transformed_data,
            "success": True,
            "metadata": {
                "transform_type": transform_type,
                "original_type": type(data).__name__,
                "transformed_type": type(transformed_data).__name__
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_filter(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        filter_criteria = config.get('criteria', {})
        data = input_data.get('data', [])
        
        if not isinstance(data, list):
            data = [data]
        
        filtered_data = []
        for item in data:
            if self._matches_filter_criteria(item, filter_criteria):
                filtered_data.append(item)
        
        return {
            "operation_type": "filter",
            "result": filtered_data,
            "success": True,
            "metadata": {
                "original_count": len(data),
                "filtered_count": len(filtered_data),
                "criteria_applied": filter_criteria
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_merge(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        merge_strategy = config.get('merge_strategy', 'overwrite')
        sources = config.get('sources', [])
        
        if not isinstance(sources, list):
            sources = [sources]
        
        merged_data = {}
        for source in sources:
            if isinstance(source, dict):
                if merge_strategy == 'overwrite':
                    merged_data.update(source)
                elif merge_strategy == 'deep':
                    merged_data = self._deep_merge(merged_data, source)
        
        return {
            "operation_type": "merge",
            "result": merged_data,
            "success": True,
            "metadata": {
                "merge_strategy": merge_strategy,
                "sources_count": len(sources),
                "result_keys": list(merged_data.keys())
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_split(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        split_field = config.get('split_field', 'items')
        data = input_data.get('data', {})
        
        if isinstance(data, dict) and split_field in data:
            split_data = data[split_field]
            if isinstance(split_data, list):
                split_result = [{split_field: [item]} for item in split_data]
            else:
                split_result = [data]
        else:
            split_result = [data]
        
        return {
            "operation_type": "split",
            "result": split_result,
            "success": True,
            "metadata": {
                "split_field": split_field,
                "split_count": len(split_result),
                "original_type": type(data).__name__
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_enrich(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        enrichment_source = config.get('source', 'static')
        enrichment_data = config.get('enrichment_data', {})
        original_data = input_data.get('data', {})
        
        if isinstance(original_data, dict):
            enriched_data = {**original_data, **enrichment_data}
        else:
            enriched_data = {
                "original": original_data,
                "enriched": enrichment_data
            }
        
        return {
            "operation_type": "enrich",
            "result": enriched_data,
            "success": True,
            "metadata": {
                "enrichment_source": enrichment_source,
                "original_keys": list(original_data.keys()) if isinstance(original_data, dict) else [],
                "enriched_keys": list(enrichment_data.keys())
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_validate(self, config: Dict[str, Any], input_data: Dict[str, Any], context: PrimitiveExecutionContext) -> Dict[str, Any]:
        validation_rules = config.get('validation_rules', {})
        data = input_data.get('data', {})
        
        validation_results = {}
        is_valid = True
        
        for field, rule in validation_rules.items():
            if isinstance(rule, dict):
                field_valid = self._validate_field(data.get(field), rule)
                validation_results[field] = field_valid
                if not field_valid['valid']:
                    is_valid = False
            else:
                # Simple required field validation
                field_valid = {
                    "valid": field in data and data[field] is not None,
                    "rule": "required"
                }
                validation_results[field] = field_valid
                if not field_valid['valid']:
                    is_valid = False
        
        return {
            "operation_type": "validate",
            "result": {
                "valid": is_valid,
                "validation_results": validation_results,
                "data": data
            },
            "success": True,
            "metadata": {
                "validation_rules_count": len(validation_rules),
                "validation_passed": is_valid
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _flatten_dict(self, data: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary"""
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _normalize_data(self, data: Any) -> Dict[str, Any]:
        """Normalize data structure to consistent format"""
        if isinstance(data, dict):
            return data
        elif isinstance(data, list):
            return {"items": data}
        elif isinstance(data, (str, int, float, bool)):
            return {"value": data}
        else:
            return {"raw": str(data)}
    
    def _matches_filter_criteria(self, item: Any, criteria: Dict[str, Any]) -> bool:
        """Check if item matches filter criteria"""
        if not isinstance(item, dict):
            return False
        
        for key, expected_value in criteria.items():
            actual_value = item.get(key)
            
            # Handle different comparison types
            if isinstance(expected_value, dict) and 'operator' in expected_value:
                operator = expected_value['operator']
                target_value = expected_value.get('value')
                
                if operator == 'equals':
                    if actual_value != target_value:
                        return False
                elif operator == 'contains':
                    if not isinstance(actual_value, str) or str(target_value) not in actual_value:
                        return False
                elif operator == 'greater_than':
                    if not isinstance(actual_value, (int, float)) or actual_value <= target_value:
                        return False
                elif operator == 'less_than':
                    if not isinstance(actual_value, (int, float)) or actual_value >= target_value:
                        return False
            else:
                # Simple equality check
                if actual_value != expected_value:
                    return False
        
        return True
    
    def _deep_merge(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _validate_field(self, value: Any, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single field against validation rules"""
        field_valid = {"valid": True, "rule": rule}
        
        if rule.get('required') and (value is None or value == ''):
            field_valid["valid"] = False
            field_valid["error"] = "Field is required"
        
        if rule.get('type') and value is not None:
            expected_type = rule['type']
            actual_type = type(value).__name__
            if expected_type != actual_type:
                field_valid["valid"] = False
                field_valid["error"] = f"Expected {expected_type}, got {actual_type}"
        
        if rule.get('min_length') and isinstance(value, str):
            if len(value) < rule['min_length']:
                field_valid["valid"] = False
                field_valid["error"] = f"Minimum length is {rule['min_length']}"
        
        return field_valid
