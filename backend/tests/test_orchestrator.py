import pytest
import asyncio
import os
from backend.orchestrator import DisasterOrchestrator


class TestDisasterOrchestrator:
    """Test cases for DisasterOrchestrator"""
    
    def test_orchestrator_initialization(self):
        """Test that orchestrator initializes correctly"""
        orchestrator = DisasterOrchestrator()
        assert orchestrator.name == "DisasterOrchestrator"
    
    @pytest.mark.asyncio
    async def test_call_llm_api_without_key(self):
        """Test that _call_llm_api handles missing API key gracefully"""
        orchestrator = DisasterOrchestrator()
        
        # Temporarily remove API key if present
        original_key = os.getenv('OPENROUTER_API_KEY')
        if original_key:
            del os.environ['OPENROUTER_API_KEY']
        
        result = await orchestrator._call_llm_api({"test": "context"})
        
        # Restore key if it existed
        if original_key:
            os.environ['OPENROUTER_API_KEY'] = original_key
        
        assert result["summary"] == "Error: LLM API key not configured."
        assert result["overview"] == ""
        assert result["templates"] == {}
    
    def test_build_master_prompt_placeholder(self):
        """Test placeholder implementation of _build_master_prompt"""
        orchestrator = DisasterOrchestrator()
        context = {"disaster_type": "fire", "location": "Test City"}
        
        prompt = orchestrator._build_master_prompt(context)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    def test_parse_llm_response_placeholder(self):
        """Test placeholder implementation of _parse_llm_response"""
        orchestrator = DisasterOrchestrator()
        response_text = "This is a test response"
        
        result = orchestrator._parse_llm_response(response_text)
        
        assert "summary" in result
        assert "overview" in result
        assert "templates" in result
        assert result["overview"] == response_text