"""
Standalone test runner for DisasterOrchestrator tests
Runs tests without requiring pytest installation
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from orchestrator import DisasterOrchestrator
from unittest.mock import AsyncMock, patch


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def run_test(self, test_name, test_func):
        """Run a single test function"""
        try:
            result = test_func()
            if asyncio.iscoroutine(result):
                asyncio.run(result)
            print(f"[PASS] {test_name}")
            self.passed += 1
            return True
        except AssertionError as e:
            print(f"[FAIL] {test_name}")
            print(f"  Error: {e}")
            self.failed += 1
            self.errors.append((test_name, str(e)))
            return False
        except Exception as e:
            print(f"[ERROR] {test_name}")
            print(f"  Error: {e}")
            self.failed += 1
            self.errors.append((test_name, str(e)))
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print(f"Test Summary: {self.passed} passed, {self.failed} failed")
        print("=" * 60)
        
        if self.errors:
            print("\nFailed Tests:")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")
        
        if self.failed == 0:
            print("\n[SUCCESS] ALL TESTS PASSED!")
            return 0
        else:
            print(f"\n[FAILURE] {self.failed} TEST(S) FAILED")
            return 1


def test_initialization():
    """Test orchestrator initialization"""
    orchestrator = DisasterOrchestrator()
    assert orchestrator.name == "DisasterOrchestrator"


async def test_call_llm_api_without_key():
    """Test _call_llm_api handles missing API key"""
    orchestrator = DisasterOrchestrator()
    original_key = os.getenv('OPENROUTER_API_KEY')
    
    if 'OPENROUTER_API_KEY' in os.environ:
        del os.environ['OPENROUTER_API_KEY']
    
    try:
        result = await orchestrator._call_llm_api({"test": "context"})
        assert result["summary"] == "Error: LLM API key not configured."
        assert result["overview"] == ""
        assert result["templates"] == {}
    finally:
        if original_key:
            os.environ['OPENROUTER_API_KEY'] = original_key


def test_build_master_prompt():
    """Test _build_master_prompt"""
    orchestrator = DisasterOrchestrator()
    context = {"disaster_type": "fire", "location": "Test City"}
    prompt = orchestrator._build_master_prompt(context)
    
    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_parse_llm_response():
    """Test _parse_llm_response"""
    orchestrator = DisasterOrchestrator()
    response_text = "This is a test response"
    result = orchestrator._parse_llm_response(response_text)
    
    assert "summary" in result
    assert "overview" in result
    assert "templates" in result
    assert result["overview"] == response_text


async def test_create_disaster():
    """Test create_disaster method"""
    orchestrator = DisasterOrchestrator()
    disaster_data = {"type": "wildfire", "location": "California"}
    result = await orchestrator.create_disaster(disaster_data)
    
    assert isinstance(result, dict)
    assert "status" in result
    assert result["status"] == "created"


async def test_process_disaster_with_mock():
    """Test process_disaster with mocked LLM"""
    orchestrator = DisasterOrchestrator()
    
    mock_plan = {
        "summary": "Test plan",
        "overview": "Test overview",
        "templates": {}
    }
    orchestrator._call_llm_api = AsyncMock(return_value=mock_plan)
    
    result = await orchestrator.process_disaster("test_id", {"test": "context"})
    assert result == mock_plan


async def test_call_llm_api_with_mock_success():
    """Test successful API call with mock"""
    orchestrator = DisasterOrchestrator()
    
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        'choices': [{'message': {'content': 'Test response'}}]
    })
    
    with patch('aiohttp.ClientSession') as mock_session:
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_session.return_value.__aenter__.return_value.post.return_value = mock_cm
        
        os.environ['OPENROUTER_API_KEY'] = 'test_key'
        
        try:
            result = await orchestrator._call_llm_api({"test": "context"})
            assert "overview" in result
        finally:
            if os.getenv('OPENROUTER_API_KEY') == 'test_key':
                del os.environ['OPENROUTER_API_KEY']


async def test_real_api_call():
    """Test real API call if key is available"""
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("  (Skipped - no API key)")
        return
    
    orchestrator = DisasterOrchestrator()
    context = {"disaster_type": "fire", "location": "Test City"}
    
    result = await orchestrator._call_llm_api(context)
    
    assert isinstance(result, dict)
    assert "summary" in result
    assert "overview" in result
    
    if "Error" not in result["summary"]:
        assert len(result["overview"]) > 0
        print(f"    Response length: {len(result['overview'])} chars")


async def test_call_llm_api_correct_headers():
    """Test that correct headers are sent"""
    orchestrator = DisasterOrchestrator()
    
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        'choices': [{'message': {'content': 'test'}}]
    })
    
    with patch('aiohttp.ClientSession') as mock_session:
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_post = mock_session.return_value.__aenter__.return_value.post
        mock_post.return_value = mock_cm
        
        os.environ['OPENROUTER_API_KEY'] = 'test_key_123'
        
        try:
            await orchestrator._call_llm_api({"test": "context"})
            
            call_kwargs = mock_post.call_args.kwargs
            assert 'headers' in call_kwargs
            assert call_kwargs['headers']['Authorization'] == 'Bearer test_key_123'
            assert call_kwargs['headers']['Content-Type'] == 'application/json'
        finally:
            if os.getenv('OPENROUTER_API_KEY') == 'test_key_123':
                del os.environ['OPENROUTER_API_KEY']


async def test_call_llm_api_correct_model():
    """Test that correct model is specified"""
    orchestrator = DisasterOrchestrator()
    
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        'choices': [{'message': {'content': 'test'}}]
    })
    
    with patch('aiohttp.ClientSession') as mock_session:
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response
        mock_post = mock_session.return_value.__aenter__.return_value.post
        mock_post.return_value = mock_cm
        
        os.environ['OPENROUTER_API_KEY'] = 'test_key'
        
        try:
            await orchestrator._call_llm_api({"test": "context"})
            
            call_kwargs = mock_post.call_args.kwargs
            assert 'json' in call_kwargs
            assert call_kwargs['json']['model'] == 'anthropic/claude-3.5-sonnet'
        finally:
            if os.getenv('OPENROUTER_API_KEY') == 'test_key':
                del os.environ['OPENROUTER_API_KEY']


def main():
    """Run all tests"""
    print("=" * 60)
    print("DisasterOrchestrator Test Suite")
    print("=" * 60)
    
    runner = TestRunner()
    
    print("\n--- Initialization Tests ---")
    runner.run_test("test_initialization", test_initialization)
    
    print("\n--- Method Tests ---")
    runner.run_test("test_build_master_prompt", test_build_master_prompt)
    runner.run_test("test_parse_llm_response", test_parse_llm_response)
    
    print("\n--- Error Handling Tests ---")
    runner.run_test("test_call_llm_api_without_key", test_call_llm_api_without_key)
    
    print("\n--- Workflow Tests ---")
    runner.run_test("test_create_disaster", test_create_disaster)
    runner.run_test("test_process_disaster_with_mock", test_process_disaster_with_mock)
    
    print("\n--- Mock API Tests ---")
    runner.run_test("test_call_llm_api_with_mock_success", test_call_llm_api_with_mock_success)
    runner.run_test("test_call_llm_api_correct_headers", test_call_llm_api_correct_headers)
    runner.run_test("test_call_llm_api_correct_model", test_call_llm_api_correct_model)
    
    print("\n--- Real API Tests ---")
    runner.run_test("test_real_api_call", test_real_api_call)
    
    return runner.print_summary()


if __name__ == "__main__":
    sys.exit(main())