#!/usr/bin/env python3
"""
Comprehensive integration test for CrewAI workflow service.
Tests all components of the CrewAI multi-agent integration.
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any

# Add paths for testing
sys.path.insert(0, '/Users/naveen/Desktop/Flov7/flov7-backend')
sys.path.insert(0, '/Users/naveen/Desktop/Flov7/flov7-backend/workflow-service')

# Import enhanced CrewAI components
from app.crewai.workflow_orchestrator import crewai_orchestrator
from app.crewai.enhanced_agents import enhanced_agent_manager
from app.crewai.enhanced_tasks import enhanced_task_manager

class CrewAIIntegrationTester:
    """Comprehensive tester for CrewAI integration"""
    
    def __init__(self):
        self.test_results = []
    
    async def test_agent_initialization(self) -> bool:
        """Test enhanced agent initialization"""
        print("\n1. Testing enhanced agent initialization...")
        
        try:
            agents = enhanced_agent_manager.get_all_agents()
            expected_agents = [
                "workflow_orchestrator", "data_analyst", "api_specialist",
                "validation_expert", "error_handler", "report_generator"
            ]
            
            found_agents = list(agents.keys())
            missing = [agent for agent in expected_agents if agent not in found_agents]
            
            if not missing:
                print("✓ All enhanced agents initialized successfully")
                print(f"  Available agents: {', '.join(found_agents)}")
                return True
            else:
                print(f"✗ Missing agents: {missing}")
                return False
                
        except Exception as e:
            print(f"✗ Agent initialization test failed: {e}")
            return False
    
    async def test_task_initialization(self) -> bool:
        """Test enhanced task initialization"""
        print("\n2. Testing enhanced task initialization...")
        
        try:
            tasks = enhanced_task_manager.get_all_tasks()
            expected_tasks = [
                "analyze_workflow_structure", "process_api_data", "transform_data",
                "validate_workflow_output", "handle_execution_errors",
                "generate_execution_report", "coordinate_multi_agent_workflow"
            ]
            
            found_tasks = list(tasks.keys())
            missing = [task for task in expected_tasks if task not in found_tasks]
            
            if not missing:
                print("✓ All enhanced tasks initialized successfully")
                print(f"  Available tasks: {', '.join(found_tasks)}")
                return True
            else:
                print(f"✗ Missing tasks: {missing}")
                return False
                
        except Exception as e:
            print(f"✗ Task initialization test failed: {e}")
            return False
    
    async def test_workflow_validation(self) -> bool:
        """Test workflow validation"""
        print("\n3. Testing workflow validation...")
        
        # Test valid workflow
        valid_workflow = {
            "id": "test-validation-001",
            "name": "Validation Test Workflow",
            "nodes": [
                {"id": "node1", "type": "api_call", "data": {"url": "https://example.com"}},
                {"id": "node2", "type": "transform", "data": {"transform_type": "mapping"}}
            ],
            "edges": [
                {"source": "node1", "target": "node2"}
            ]
        }
        
        try:
            result = await crewai_orchestrator._validate_workflow_structure(valid_workflow)
            
            if result["valid"]:
                print("✓ Valid workflow structure accepted")
                return True
            else:
                print(f"✗ Valid workflow rejected: {result['issues']}")
                return False
                
        except Exception as e:
            print(f"✗ Workflow validation test failed: {e}")
            return False
    
    async def test_invalid_workflow_detection(self) -> bool:
        """Test invalid workflow detection"""
        print("\n4. Testing invalid workflow detection...")
        
        # Test invalid workflow (cycle)
        invalid_workflow = {
            "id": "test-invalid-001",
            "name": "Invalid Workflow",
            "nodes": [
                {"id": "node1", "type": "api_call"},
                {"id": "node2", "type": "transform"}
            ],
            "edges": [
                {"source": "node1", "target": "node2"},
                {"source": "node2", "target": "node1"}  # Creates cycle
            ]
        }
        
        try:
            result = await crewai_orchestrator._validate_workflow_structure(invalid_workflow)
            
            if not result["valid"] and "cycles" in str(result["issues"]):
                print("✓ Invalid workflow (cycle) correctly detected")
                return True
            else:
                print(f"✗ Invalid workflow not detected: {result}")
                return False
                
        except Exception as e:
            print(f"✗ Invalid workflow detection test failed: {e}")
            return False
    
    async def test_execution_plan_creation(self) -> bool:
        """Test execution plan creation"""
        print("\n5. Testing execution plan creation...")
        
        workflow = {
            "id": "test-plan-001",
            "name": "Plan Test Workflow",
            "nodes": [
                {"id": "start", "type": "api_call"},
                {"id": "process", "type": "transform"},
                {"id": "end", "type": "validation"}
            ],
            "edges": [
                {"source": "start", "target": "process"},
                {"source": "process", "target": "end"}
            ]
        }
        
        try:
            plan = await crewai_orchestrator._create_execution_plan(workflow)
            
            if plan["execution_order"] and plan["phases"]:
                print("✓ Execution plan created successfully")
                print(f"  Execution order: {plan['execution_order']}")
                print(f"  Phases: {len(plan['phases'])}")
                return True
            else:
                print("✗ Execution plan creation failed")
                return False
                
        except Exception as e:
            print(f"✗ Execution plan creation test failed: {e}")
            return False
    
    async def test_node_task_creation(self) -> bool:
        """Test node-specific task creation"""
        print("\n6. Testing node-specific task creation...")
        
        test_node = {
            "id": "test-node-001",
            "type": "api_call",
            "data": {
                "url": "https://api.example.com/data",
                "method": "GET"
            }
        }
        
        try:
            tasks = enhanced_task_manager.create_workflow_specific_tasks({
                "nodes": [test_node],
                "type": "api_workflow"
            })
            
            if tasks and len(tasks) > 0:
                print("✓ Node-specific tasks created successfully")
                print(f"  Created {len(tasks)} tasks for single node")
                return True
            else:
                print("✗ Node-specific task creation failed")
                return False
                
        except Exception as e:
            print(f"✗ Node task creation test failed: {e}")
            return False
    
    async def test_simple_workflow_simulation(self) -> bool:
        """Test simple workflow simulation"""
        print("\n7. Testing simple workflow simulation...")
        
        simple_workflow = {
            "id": "simple-test-001",
            "name": "Simple Test Workflow",
            "type": "simple",
            "nodes": [
                {
                    "id": "fetch",
                    "type": "api_call",
                    "data": {
                        "url": "https://jsonplaceholder.typicode.com/posts/1",
                        "method": "GET"
                    }
                },
                {
                    "id": "process",
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
                {"source": "fetch", "target": "process"}
            ]
        }
        
        try:
            # Test execution plan
            plan = await crewai_orchestrator._create_execution_plan(simple_workflow)
            
            # Test phase execution
            phase_results = await crewai_orchestrator._execute_workflow_phases(
                simple_workflow, plan
            )
            
            if phase_results:
                print("✓ Simple workflow simulation completed")
                print(f"  Phases executed: {len(phase_results)}")
                return True
            else:
                print("✗ Simple workflow simulation failed")
                return False
                
        except Exception as e:
            print(f"✗ Simple workflow simulation test failed: {e}")
            return False
    
    async def test_agent_selection(self) -> bool:
        """Test agent selection for different node types"""
        print("\n8. Testing agent selection...")
        
        test_cases = [
            ("api_call", "api_specialist"),
            ("transform", "data_analyst"),
            ("validation", "validation_expert"),
            ("unknown", "workflow_orchestrator")
        ]
        
        try:
            agents = enhanced_agent_manager.get_agents_for_workflow("test")
            
            for node_type, expected_agent in test_cases:
                selected = enhanced_task_manager._select_agent_for_node_type(node_type, agents)
                if selected:
                    print(f"✓ {node_type} -> {selected.role}")
                else:
                    print(f"✗ {node_type} -> no agent selected")
            
            return True
            
        except Exception as e:
            print(f"✗ Agent selection test failed: {e}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling"""
        print("\n9. Testing error handling...")
        
        try:
            # Test with empty workflow
            empty_workflow = {"id": "empty-test", "name": "Empty Test"}
            
            result = await crewai_orchestrator._validate_workflow_structure(empty_workflow)
            
            if not result["valid"] and "No workflow nodes provided" in str(result["issues"]):
                print("✓ Error handling for empty workflow working")
                return True
            else:
                print("✗ Error handling test failed")
                return False
                
        except Exception as e:
            print(f"✗ Error handling test failed: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all CrewAI integration tests"""
        print("=" * 60)
        print("CREWAI INTEGRATION TESTS")
        print("=" * 60)
        
        tests = [
            self.test_agent_initialization,
            self.test_task_initialization,
            self.test_workflow_validation,
            self.test_invalid_workflow_detection,
            self.test_execution_plan_creation,
            self.test_node_task_creation,
            self.test_simple_workflow_simulation,
            self.test_agent_selection,
            self.test_error_handling
        ]
        
        results = {}
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                result = await test()
                results[test.__name__] = result
                if result:
                    passed += 1
            except Exception as e:
                print(f"✗ {test.__name__} failed with exception: {e}")
                results[test.__name__] = False
        
        print("\n" + "=" * 60)
        print(f"CREWAI TEST RESULTS: {passed}/{total} passed")
        print("=" * 60)
        
        for test_name, passed_test in results.items():
            status = "✓ PASS" if passed_test else "✗ FAIL"
            print(f"{test_name}: {status}")
        
        return results

async def main():
    """Main test runner"""
    tester = CrewAIIntegrationTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    passed = sum(results.values())
    total = len(results)
    
    if passed == total:
        print("\n🎉 All CrewAI integration tests passed!")
        print("\nNext steps:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Start workflow service")
        print("3. Test with real workflows")
        return 0
    else:
        print(f"\n❌ {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
