"""
Tests for BaseAgent abstract class
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from typing import Dict, Any
from agents.base_agent import BaseAgent


class ConcreteAgent(BaseAgent):
    """A concrete implementation of BaseAgent for testing"""
    
    async def analyze(self, *args, **kwargs) -> Dict[str, Any]:
        """Implementation of the abstract analyze method"""
        self._log("Running analysis")
        return {
            "status": "success",
            "data": "analysis complete",
            "args": args,
            "kwargs": kwargs
        }


class IncompleteAgent(BaseAgent):
    """An incomplete implementation (missing analyze method)"""
    pass


def test_base_agent_cannot_be_instantiated():
    """Test that BaseAgent cannot be instantiated directly"""
    print("\n=== Test 1: BaseAgent Cannot Be Instantiated ===")
    try:
        agent = BaseAgent()
        print("❌ FAILED: BaseAgent was instantiated (should raise TypeError)")
        return False
    except TypeError as e:
        print(f"✓ PASSED: BaseAgent cannot be instantiated (as expected)")
        print(f"  Expected TypeError raised: {e}")
        return True


def test_incomplete_agent_cannot_be_instantiated():
    """Test that incomplete implementations cannot be instantiated"""
    print("\n=== Test 2: Incomplete Agent Cannot Be Instantiated ===")
    try:
        agent = IncompleteAgent()
        print("❌ FAILED: IncompleteAgent was instantiated (should raise TypeError)")
        return False
    except TypeError as e:
        print(f"✓ PASSED: IncompleteAgent cannot be instantiated (as expected)")
        print(f"  Expected TypeError raised: {e}")
        return True


def test_concrete_agent_can_be_instantiated():
    """Test that a concrete implementation can be instantiated"""
    print("\n=== Test 3: Concrete Agent Can Be Instantiated ===")
    try:
        agent = ConcreteAgent()
        print(f"✓ PASSED: ConcreteAgent instantiated successfully")
        print(f"  Agent name: {agent.name}")
        return agent.name == "ConcreteAgent"
    except Exception as e:
        print(f"❌ FAILED: Could not instantiate ConcreteAgent: {e}")
        return False


async def test_analyze_method():
    """Test that the analyze method works correctly"""
    print("\n=== Test 4: Analyze Method Works ===")
    try:
        agent = ConcreteAgent()
        result = await agent.analyze("test_data", param1="value1")
        
        assert result["status"] == "success", "Status should be 'success'"
        assert result["data"] == "analysis complete", "Data should match expected value"
        assert result["args"] == ("test_data",), "Args should be captured"
        assert result["kwargs"] == {"param1": "value1"}, "Kwargs should be captured"
        
        print(f"✓ PASSED: Analyze method works correctly")
        print(f"  Result: {result}")
        return True
    except Exception as e:
        print(f"❌ FAILED: Analyze method failed: {e}")
        return False


def test_log_method():
    """Test that the _log method works correctly"""
    print("\n=== Test 5: Log Method Works ===")
    try:
        agent = ConcreteAgent()
        print(f"  Testing log output:")
        agent._log("This is a test message")
        print(f"✓ PASSED: Log method works correctly")
        return True
    except Exception as e:
        print(f"❌ FAILED: Log method failed: {e}")
        return False


def test_inheritance():
    """Test that inheritance properties work correctly"""
    print("\n=== Test 6: Inheritance Properties ===")
    try:
        agent = ConcreteAgent()
        
        # Check if it's an instance of BaseAgent
        assert isinstance(agent, BaseAgent), "ConcreteAgent should be instance of BaseAgent"
        
        # Check if it has all required methods
        assert hasattr(agent, 'analyze'), "Should have analyze method"
        assert hasattr(agent, '_log'), "Should have _log method"
        assert hasattr(agent, 'name'), "Should have name attribute"
        
        print(f"✓ PASSED: Inheritance properties are correct")
        print(f"  Is instance of BaseAgent: {isinstance(agent, BaseAgent)}")
        print(f"  Has analyze method: {hasattr(agent, 'analyze')}")
        print(f"  Has _log method: {hasattr(agent, '_log')}")
        print(f"  Has name attribute: {hasattr(agent, 'name')}")
        return True
    except Exception as e:
        print(f"❌ FAILED: Inheritance test failed: {e}")
        return False


async def run_async_tests():
    """Run all async tests"""
    results = []
    results.append(await test_analyze_method())
    return all(results)


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing BaseAgent Abstract Class")
    print("=" * 60)
    
    results = []
    
    # Synchronous tests
    results.append(test_base_agent_cannot_be_instantiated())
    results.append(test_incomplete_agent_cannot_be_instantiated())
    results.append(test_concrete_agent_can_be_instantiated())
    results.append(test_log_method())
    results.append(test_inheritance())
    
    # Async tests
    async_result = asyncio.run(run_async_tests())
    results.append(async_result)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("✓ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    
    print("=" * 60)


if __name__ == "__main__":
    main()