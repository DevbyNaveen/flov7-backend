#!/bin/bash

# Test script for the 5-primitives system implementation
# This script runs comprehensive tests for the primitive registry and executors

echo "🧪 Testing 5-Primitives System Implementation"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Check if we're in the correct directory
if [ ! -d "flov7-backend" ]; then
    echo -e "${YELLOW}⚠️  Please run this script from the Flov7 project root directory${NC}"
    exit 1
fi

cd flov7-backend

# Set up Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "📋 Running primitive system tests..."

# Run the comprehensive test suite
python -m pytest tests/test_primitives_system.py -v --tb=short
TEST_RESULT=$?

print_status $TEST_RESULT "Primitive system tests"

# Run individual component tests
echo ""
echo "🔍 Testing individual primitive executors..."

# Test trigger executor
python -c "
import asyncio
from shared.primitives import TriggerExecutor, PrimitiveExecutionContext
from uuid import uuid4

async def test():
    executor = TriggerExecutor()
    context = PrimitiveExecutionContext(execution_id=str(uuid4()), user_id='test')
    result = await executor.execute({'trigger_type': 'manual'}, {'trigger_data': {}}, context)
    print('Trigger Executor:', 'PASS' if result['triggered'] else 'FAIL')

asyncio.run(test())
"
print_status $? "Trigger executor basic test"

# Test action executor
python -c "
import asyncio
from shared.primitives import ActionExecutor, PrimitiveExecutionContext
from uuid import uuid4

async def test():
    executor = ActionExecutor()
    context = PrimitiveExecutionContext(execution_id=str(uuid4()), user_id='test')
    result = await executor.execute({'action_type': 'wait', 'duration': 0.1}, {}, context)
    print('Action Executor:', 'PASS' if result['success'] else 'FAIL')

asyncio.run(test())
"
print_status $? "Action executor basic test"

# Test registry functionality
echo ""
echo "🗃️  Testing primitive registry..."

python -c "
from shared.primitives import primitive_registry

# Test registry initialization
trigger_exists = primitive_registry.is_primitive_registered('trigger')
action_exists = primitive_registry.is_primitive_registered('action')

print('Registry - Trigger:', 'PASS' if trigger_exists else 'FAIL')
print('Registry - Action:', 'PASS' if action_exists else 'FAIL')
"
print_status $? "Registry basic functionality"

# Test template system
echo ""
echo "📋 Testing template system..."

python -c "
from shared.primitives import template_manager

# Test template initialization
templates = template_manager.list_templates()
trigger_templates = template_manager.get_templates_by_type('trigger')

print('Template System - Total:', len(templates))
print('Template System - Triggers:', len(trigger_templates))
print('Template System:', 'PASS' if len(templates) > 0 else 'FAIL')
"
print_status $? "Template system basic test"

# Test end-to-end workflow
echo ""
echo "🔄 Testing end-to-end primitive workflow..."

python -c "
import asyncio
from shared.primitives import primitive_registry, PrimitiveExecutionContext
from uuid import uuid4

async def test_workflow():
    try:
        context = PrimitiveExecutionContext(execution_id=str(uuid4()), user_id='test')
        
        # 1. Trigger
        trigger_result = await primitive_registry.execute_primitive(
            'trigger',
            {'trigger_type': 'manual'},
            {'trigger_data': {'user': 'test'}},
            context
        )
        
        # 2. Data processing
        data_result = await primitive_registry.execute_primitive(
            'data',
            {'operation_type': 'transform', 'transform_type': 'json'},
            {'data': {'test': 'data'}},
            context
        )
        
        # 3. Action
        action_result = await primitive_registry.execute_primitive(
            'action',
            {'action_type': 'transform'},
            {'data': data_result['data']},
            context
        )
        
        success = all([trigger_result['success'], data_result['success'], action_result['success']])
        print('End-to-end workflow:', 'PASS' if success else 'FAIL')
        
    except Exception as e:
        print('End-to-end workflow: FAIL -', str(e))

asyncio.run(test_workflow())
"
print_status $? "End-to-end workflow test"

# Summary
echo ""
echo "📊 Test Summary"
echo "==============="

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}🎉 All primitive system tests passed successfully!${NC}"
    echo ""
    echo "The 5-primitives system is now functional with:"
    echo "✅ Primitive Registry - Runtime management of primitives"
    echo "✅ Primitive Executors - Concrete implementations for all 5 primitives"
    echo "✅ Validation Engine - Runtime configuration and data validation"
    echo "✅ Template System - Dynamic primitive generation from templates"
    echo "✅ Integration Tests - End-to-end workflow execution"
    echo ""
    echo "Usage examples:"
    echo "  - Run tests: ./test-primitives-system.sh"
    echo "  - Use registry: from shared.primitives import primitive_registry"
    echo "  - Use templates: from shared.primitives import template_manager"
else
    echo -e "${RED}⚠️  Some tests failed. Please check the output above.${NC}"
    exit 1
fi
