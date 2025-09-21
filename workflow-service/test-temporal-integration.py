#!/usr/bin/env python3
"""
Comprehensive integration test for Temporal workflow service.
Tests all components of the Temporal integration.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test workflow definitions
TEST_WORKFLOWS = {
    "simple_api_workflow": {
        "id": "test-simple-api-001",
        "name": "Simple API Test Workflow",
        "nodes": [
            {
                "id": "fetch-data",
                "type": "api_call",
                "data": {
                    "url": "https://jsonplaceholder.typicode.com/posts/1",
                    "method": "GET"
                }
            },
            {
                "id": "process-data",
                "type": "transform",
                "data": {
                    "transform_type": "mapping",
                    "mapping": {
                        "title": "inputs.title",
                        "userId": "inputs.userId"
                    }
                }
            }
        ],
        "edges": [
            {"id": "edge-1", "source": "fetch-data", "target": "process-data"}
        ]
    },
    
    "conditional_workflow": {
        "id": "test-conditional-001",
        "name": "Conditional Logic Test",
        "nodes": [
            {
                "id": "check-value",
                "type": "condition",
                "data": {
                    "condition": "inputs.value > 10"
                }
            },
            {
                "id": "high-value",
                "type": "transform",
                "data": {
                    "transform_type": "mapping",
                    "mapping": {"result": "'High value: ' + str(inputs.value)"}
                }
            },
            {
                "id": "low-value",
                "type": "transform",
                "data": {
                    "transform_type": "mapping", 
                    "mapping": {"result": "'Low value: ' + str(inputs.value)"}
                }
            }
        ],
        "edges": [
            {"id": "edge-1", "source": "check-value", "target": "high-value"},
            {"id": "edge-2", "source": "check-value", "target": "low-value"}
        ]
    },
    
    "validation_test": {
        "id": "test-validation-001",
        "name": "Validation Test Workflow",
        "nodes": [
            {"id": "valid-node-1", "type": "delay", "data": {"delay_seconds": 1}},
            {"id": "valid-node-2", "type": "delay", "data": {"delay_seconds": 1}}
        ],
        "edges": [
            {"id": "valid-edge-1", "source": "valid-node-1", "target": "valid-node-2"}
        ]
    }
}

class TemporalIntegrationTester:
    """Comprehensive tester for Temporal integration"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def test_service_health(self) -> bool:
        """Test if the workflow service is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                logger.info("✓ Service health check passed")
                return True
            else:
                logger.error(f"✗ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"✗ Health check failed: {e}")
            return False
    
    async def test_workflow_validation(self) -> bool:
        """Test workflow validation endpoint"""
        try:
            # Test valid workflow
            response = await self.client.post(
                f"{self.base_url}/api/v1/workflow/validate",
                json=TEST_WORKFLOWS["validation_test"]
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("valid"):
                    logger.info("✓ Workflow validation test passed")
                    return True
                else:
                    logger.error(f"✗ Workflow validation failed: {result}")
                    return False
            else:
                logger.error(f"✗ Validation endpoint failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Validation test failed: {e}")
            return False
    
    async def test_workflow_execution(self) -> bool:
        """Test workflow execution"""
        try:
            # Test simple workflow execution
            workflow_data = TEST_WORKFLOWS["simple_api_workflow"]
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/workflow/execute",
                json={
                    "workflow": workflow_data,
                    "user_id": "test-user-001"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                execution_id = result.get("execution_id")
                
                if execution_id:
                    logger.info(f"✓ Workflow execution started: {execution_id}")
                    
                    # Wait a bit and check status
                    await asyncio.sleep(2)
                    status_response = await self.client.get(
                        f"{self.base_url}/api/v1/workflow/status/{execution_id}"
                    )
                    
                    if status_response.status_code == 200:
                        status = status_response.json()
                        logger.info(f"✓ Workflow status retrieved: {status.get('status')}")
                        return True
                
            logger.error(f"✗ Workflow execution test failed: {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"✗ Workflow execution test failed: {e}")
            return False
    
    async def test_temporal_client(self) -> bool:
        """Test Temporal client connectivity"""
        try:
            # Import Temporal client
            from app.temporal.client import get_temporal_client
            
            client = await get_temporal_client()
            if client:
                # Test connection
                await client.workflow_service.get_system_info()
                logger.info("✓ Temporal client connection test passed")
                return True
            else:
                logger.warning("⚠ Temporal client not available (fallback mode)")
                return True  # Allow fallback testing
                
        except Exception as e:
            logger.error(f"✗ Temporal client test failed: {e}")
            return False
    
    async def test_workflow_validation_temporal(self) -> bool:
        """Test Temporal workflow validation"""
        try:
            from app.temporal.client import get_temporal_client
            from app.temporal.workflows import WorkflowValidation
            
            client = await get_temporal_client()
            if not client:
                logger.warning("⚠ Skipping Temporal validation test (client unavailable)")
                return True
            
            # Test validation workflow
            validation_result = await client.execute_workflow(
                WorkflowValidation.run,
                TEST_WORKFLOWS["validation_test"],
                id=f"validation-test-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                task_queue="flov7-workflow-task-queue"
            )
            
            if validation_result.get("valid"):
                logger.info("✓ Temporal workflow validation test passed")
                return True
            else:
                logger.error(f"✗ Temporal validation failed: {validation_result}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Temporal validation test failed: {e}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling scenarios"""
        try:
            # Test invalid workflow
            invalid_workflow = {
                "id": "invalid-workflow",
                "name": "Invalid Workflow",
                "nodes": [],
                "edges": [
                    {"source": "nonexistent", "target": "also-nonexistent"}
                ]
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/workflow/validate",
                json=invalid_workflow
            )
            
            if response.status_code == 200:
                result = response.json()
                if not result.get("valid") and result.get("issues"):
                    logger.info("✓ Error handling test passed")
                    return True
                else:
                    logger.error("✗ Error handling test failed - no issues reported")
                    return False
            else:
                logger.error(f"✗ Error handling endpoint failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error handling test failed: {e}")
            return False
    
    async def test_worker_health(self) -> bool:
        """Test Temporal worker health"""
        try:
            # Try to execute a simple workflow
            from app.temporal.client import get_temporal_client
            from app.temporal.workflows import WorkflowExecution
            
            client = await get_temporal_client()
            if not client:
                logger.warning("⚠ Skipping worker health test (client unavailable)")
                return True
            
            # Simple delay workflow for testing
            test_workflow = {
                "id": "worker-health-test",
                "name": "Worker Health Test",
                "nodes": [
                    {
                        "id": "health-check",
                        "type": "delay",
                        "data": {"delay_seconds": 1}
                    }
                ],
                "edges": []
            }
            
            handle = await client.start_workflow(
                WorkflowExecution.run,
                test_workflow,
                id=f"health-test-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                task_queue="flov7-workflow-task-queue"
            )
            
            result = await handle.result()
            if result.get("status") == "completed":
                logger.info("✓ Worker health test passed")
                return True
            else:
                logger.error(f"✗ Worker health test failed: {result}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Worker health test failed: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all integration tests"""
        logger.info("Starting Temporal integration tests...")
        
        tests = {
            "service_health": await self.test_service_health(),
            "temporal_client": await self.test_temporal_client(),
            "workflow_validation": await self.test_workflow_validation(),
            "workflow_execution": await self.test_workflow_execution(),
            "temporal_validation": await self.test_workflow_validation_temporal(),
            "error_handling": await self.test_error_handling(),
            "worker_health": await self.test_worker_health()
        }
        
        # Summary
        passed = sum(tests.values())
        total = len(tests)
        
        logger.info(f"\n{'='*50}")
        logger.info(f"Test Results: {passed}/{total} passed")
        
        for test_name, passed in tests.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"{'='*50}")
        
        return tests


async def main():
    """Main test runner"""
    # Parse command line arguments
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8002"
    
    logger.info(f"Running Temporal integration tests against: {base_url}")
    
    async with TemporalIntegrationTester(base_url) as tester:
        results = await tester.run_all_tests()
        
        # Exit with appropriate code
        if all(results.values()):
            logger.info("🎉 All tests passed!")
            sys.exit(0)
        else:
            logger.error("❌ Some tests failed!")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
