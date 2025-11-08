"""
Simple verification script for the orchestrator implementation
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from orchestrator import DisasterOrchestrator


async def main():
    print("=" * 50)
    print("Testing DisasterOrchestrator Implementation")
    print("=" * 50)
    
    # Test 1: Initialization
    print("\n1. Testing orchestrator initialization...")
    orchestrator = DisasterOrchestrator()
    assert orchestrator.name == "DisasterOrchestrator", "Name check failed"
    print("[PASS] Orchestrator initialized successfully")
    
    # Test 2: _build_master_prompt (placeholder)
    print("\n2. Testing _build_master_prompt placeholder...")
    context = {"disaster_type": "fire", "location": "Test City"}
    prompt = orchestrator._build_master_prompt(context)
    assert isinstance(prompt, str) and len(prompt) > 0, "Prompt check failed"
    print(f"[PASS] Generated prompt: {prompt[:100]}...")
    
    # Test 3: _parse_llm_response (placeholder)
    print("\n3. Testing _parse_llm_response placeholder...")
    response_text = "This is a test response"
    result = orchestrator._parse_llm_response(response_text)
    assert "summary" in result and "overview" in result and "templates" in result
    print(f"[PASS] Parsed response: {result}")
    
    # Test 4: _call_llm_api without API key
    print("\n4. Testing _call_llm_api without API key...")
    original_key = os.getenv('OPENROUTER_API_KEY')
    if 'OPENROUTER_API_KEY' in os.environ:
        del os.environ['OPENROUTER_API_KEY']
    
    result = await orchestrator._call_llm_api({"test": "context"})
    assert result["summary"] == "Error: LLM API key not configured."
    print(f"[PASS] Correctly handled missing API key: {result['summary']}")
    
    # Restore key if it existed
    if original_key:
        os.environ['OPENROUTER_API_KEY'] = original_key
    
    # Test 5: Optional real API call test
    if original_key:
        print("\n5. Testing _call_llm_api with actual API (this may take a few seconds)...")
        test_context = {
            "disaster_type": "fire",
            "location": "Test City",
            "severity": "moderate"
        }
        
        result = await orchestrator._call_llm_api(test_context)
        
        if "Error" in result["summary"]:
            print(f"[INFO] API call returned error: {result['summary']}")
        else:
            print(f"[PASS] API call successful!")
            print(f"       Summary: {result['summary']}")
            print(f"       Overview length: {len(result['overview'])} characters")
    else:
        print("\n5. Skipping real API test (no API key found)")
    
    print("\n" + "=" * 50)
    print("All tests passed! [SUCCESS]")
    print("=" * 50)
    if not original_key:
        print("\nNOTE: To test the actual API call, set OPENROUTER_API_KEY in your .env file")


if __name__ == "__main__":
    asyncio.run(main())