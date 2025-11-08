import pytest
import asyncio
import os
import json
from unittest.mock import AsyncMock, patch, MagicMock
from backend.orchestrator import DisasterOrchestrator


class TestDisasterOrchestratorInitialization:
    """Test orchestrator initialization and basic setup"""
    
    def test_orchestrator_initialization(self):
        """Test that orchestrator initializes correctly"""
        orchestrator = DisasterOrchestrator()
        assert orchestrator.name == "DisasterOrchestrator"
        assert hasattr(orchestrator, '_log')
    
    def test_orchestrator_log_method(self, capsys):
        """Test that logging works correctly"""
        orchestrator = DisasterOrchestrator()
        orchestrator._log("Test message")
        captured = capsys.readouterr()
        assert "[DisasterOrchestrator]" in captured.out
        assert "Test message" in captured.out


class TestBuildMasterPrompt:
    """Test _build_master_prompt method"""
    
    def test_build_master_prompt_basic(self):
        """Test basic prompt building with simple context"""
        orchestrator = DisasterOrchestrator()
        context = {"disaster_type": "fire", "location": "Test City"}
        
        prompt = orchestrator._build_master_prompt(context)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "fire" in prompt.lower()
        assert "Test City" in prompt
    
    def test_build_master_prompt_complex_context(self):
        """Test prompt building with complex context"""
        orchestrator = DisasterOrchestrator()
        context = {
            "disaster_type": "wildfire",
            "location": "Northern California",
            "severity": "high",
            "weather": {"temp": 35, "humidity": 15, "wind_speed": 40}
        }
        
        prompt = orchestrator._build_master_prompt(context)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "wildfire" in prompt.lower() or "fire" in prompt.lower()
    
    def test_build_master_prompt_empty_context(self):
        """Test prompt building with empty context"""
        orchestrator = DisasterOrchestrator()
        context = {}
        
        prompt = orchestrator._build_master_prompt(context)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0


class TestParseLLMResponse:
    """Test _parse_llm_response method"""
    
    def test_parse_llm_response_basic(self):
        """Test basic LLM response parsing"""
        orchestrator = DisasterOrchestrator()
        response_text = "This is a test response from the LLM"
        
        result = orchestrator._parse_llm_response(response_text)
        
        assert isinstance(result, dict)
        assert "summary" in result
        assert "overview" in result
        assert "templates" in result
        assert result["overview"] == response_text
    
    def test_parse_llm_response_long_text(self):
        """Test parsing of long LLM response"""
        orchestrator = DisasterOrchestrator()
        response_text = "A" * 5000  # Long response
        
        result = orchestrator._parse_llm_response(response_text)
        
        assert isinstance(result, dict)
        assert len(result["overview"]) == 5000
    
    def test_parse_llm_response_empty_string(self):
        """Test parsing empty response"""
        orchestrator = DisasterOrchestrator()
        response_text = ""
        
        result = orchestrator._parse_llm_response(response_text)
        
        assert isinstance(result, dict)
        assert "summary" in result
        assert "overview" in result


class TestCallLLMAPIErrorHandling:
    """Test _call_llm_api error handling"""
    
    @pytest.mark.asyncio
    async def test_call_llm_api_without_key(self):
        """Test that _call_llm_api handles missing API key gracefully"""
        orchestrator = DisasterOrchestrator()
        
        # Temporarily remove API key if present
        original_key = os.getenv('OPENROUTER_API_KEY')
        if 'OPENROUTER_API_KEY' in os.environ:
            del os.environ['OPENROUTER_API_KEY']
        
        try:
            result = await orchestrator._call_llm_api({"test": "context"})
            
            assert result["summary"] == "Error: LLM API key not configured."
            assert result["overview"] == ""
            assert result["templates"] == {}
        finally:
            # Restore key if it existed
            if original_key:
                os.environ['OPENROUTER_API_KEY'] = original_key
    
    @pytest.mark.asyncio
    async def test_call_llm_api_network_error(self):
        """Test handling of network errors"""
        orchestrator = DisasterOrchestrator()
        
        # Mock aiohttp to raise a network error
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.side_effect = Exception("Network error")
            
            # Set a fake API key
            os.environ['OPENROUTER_API_KEY'] = 'test_key'
            
            try:
                result = await orchestrator._call_llm_api({"test": "context"})
                
                assert "Error" in result["summary"]
                assert result["overview"] == ""
                assert result["templates"] == {}
            finally:
                # Clean up
                if os.getenv('OPENROUTER_API_KEY') == 'test_key':
                    del os.environ['OPENROUTER_API_KEY']
    
    @pytest.mark.asyncio
    async def test_call_llm_api_http_error(self):
        """Test handling of HTTP errors (non-200 status)"""
        orchestrator = DisasterOrchestrator()
        
        # Mock aiohttp to return error status
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = mock_response
            mock_session.return_value.__aenter__.return_value.post.return_value = mock_cm
            
            # Set a fake API key
            os.environ['OPENROUTER_API_KEY'] = 'test_key'
            
            try:
                result = await orchestrator._call_llm_api({"test": "context"})
                
                assert "Error" in result["summary"]
                assert "failed" in result["summary"].lower()
            finally:
                # Clean up
                if os.getenv('OPENROUTER_API_KEY') == 'test_key':
                    del os.environ['OPENROUTER_API_KEY']
    
    @pytest.mark.asyncio
    async def test_call_llm_api_invalid_json_response(self):
        """Test handling of invalid JSON response"""
        orchestrator = DisasterOrchestrator()
        
        # Mock aiohttp to return invalid JSON
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = mock_response
            mock_session.return_value.__aenter__.return_value.post.return_value = mock_cm
            
            # Set a fake API key
            os.environ['OPENROUTER_API_KEY'] = 'test_key'
            
            try:
                result = await orchestrator._call_llm_api({"test": "context"})
                
                assert "Error" in result["summary"]
            finally:
                # Clean up
                if os.getenv('OPENROUTER_API_KEY') == 'test_key':
                    del os.environ['OPENROUTER_API_KEY']


class TestCallLLMAPISuccess:
    """Test successful _call_llm_api calls"""
    
    @pytest.mark.asyncio
    async def test_call_llm_api_successful_mock(self):
        """Test successful API call with mocked response"""
        orchestrator = DisasterOrchestrator()
        
        # Mock successful API response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'choices': [{
                'message': {
                    'content': 'This is a test response from the LLM API'
                }
            }]
        })
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = mock_response
            mock_session.return_value.__aenter__.return_value.post.return_value = mock_cm
            
            # Set a fake API key
            os.environ['OPENROUTER_API_KEY'] = 'test_key'
            
            try:
                result = await orchestrator._call_llm_api({"test": "context"})
                
                assert "summary" in result
                assert "overview" in result
                assert result["overview"] == 'This is a test response from the LLM API'
            finally:
                # Clean up
                if os.getenv('OPENROUTER_API_KEY') == 'test_key':
                    del os.environ['OPENROUTER_API_KEY']
    
    @pytest.mark.asyncio
    async def test_call_llm_api_correct_headers(self):
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
                
                # Verify correct headers were used
                call_kwargs = mock_post.call_args.kwargs
                assert 'headers' in call_kwargs
                assert call_kwargs['headers']['Authorization'] == 'Bearer test_key_123'
                assert call_kwargs['headers']['Content-Type'] == 'application/json'
            finally:
                if os.getenv('OPENROUTER_API_KEY') == 'test_key_123':
                    del os.environ['OPENROUTER_API_KEY']
    
    @pytest.mark.asyncio
    async def test_call_llm_api_correct_endpoint(self):
        """Test that correct endpoint is called"""
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
                
                # Verify correct endpoint
                call_args = mock_post.call_args
                assert call_args[0][0] == 'https://openrouter.ai/api/v1/chat/completions'
            finally:
                if os.getenv('OPENROUTER_API_KEY') == 'test_key':
                    del os.environ['OPENROUTER_API_KEY']
    
    @pytest.mark.asyncio
    async def test_call_llm_api_correct_model(self):
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
                
                # Verify correct model
                call_kwargs = mock_post.call_args.kwargs
                assert 'json' in call_kwargs
                assert call_kwargs['json']['model'] == 'anthropic/claude-3.5-sonnet'
            finally:
                if os.getenv('OPENROUTER_API_KEY') == 'test_key':
                    del os.environ['OPENROUTER_API_KEY']


class TestCreateAndProcessDisaster:
    """Test create_disaster and process_disaster methods"""
    
    @pytest.mark.asyncio
    async def test_create_disaster_basic(self):
        """Test basic disaster creation"""
        orchestrator = DisasterOrchestrator()
        disaster_data = {
            "type": "wildfire",
            "location": "California"
        }
        
        result = await orchestrator.create_disaster(disaster_data)
        
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] == "created"
    
    @pytest.mark.asyncio
    async def test_process_disaster_with_mock_llm(self):
        """Test disaster processing with mocked LLM call"""
        orchestrator = DisasterOrchestrator()
        
        # Mock the _call_llm_api method
        mock_plan = {
            "summary": "Test plan generated",
            "overview": "This is a test disaster response plan",
            "templates": {}
        }
        orchestrator._call_llm_api = AsyncMock(return_value=mock_plan)
        
        result = await orchestrator.process_disaster("test_id", {"test": "context"})
        
        assert result == mock_plan
        assert result["summary"] == "Test plan generated"


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_without_api(self):
        """Test complete workflow with mocked components"""
        orchestrator = DisasterOrchestrator()
        
        # Step 1: Create disaster
        disaster_data = {
            "type": "wildfire",
            "location": "Northern California",
            "severity": "high"
        }
        create_result = await orchestrator.create_disaster(disaster_data)
        assert create_result["status"] == "created"
        
        # Step 2: Process disaster (with mocked LLM)
        mock_plan = {
            "summary": "Comprehensive wildfire response plan",
            "overview": "Detailed response procedures...",
            "templates": {"evacuation": "...", "resources": "..."}
        }
        orchestrator._call_llm_api = AsyncMock(return_value=mock_plan)
        
        context = {
            "disaster_type": "wildfire",
            "location": "Northern California",
            "weather_data": {"temp": 35, "humidity": 15}
        }
        process_result = await orchestrator.process_disaster("test_id", context)
        
        assert process_result["summary"] == "Comprehensive wildfire response plan"
        assert "overview" in process_result


@pytest.mark.skipif(
    not os.getenv('OPENROUTER_API_KEY'),
    reason="Skipping real API test - OPENROUTER_API_KEY not set"
)
class TestRealAPIIntegration:
    """Real API integration tests (only run if API key is available)"""
    
    @pytest.mark.asyncio
    async def test_real_api_call(self):
        """Test actual API call to OpenRouter (requires API key)"""
        orchestrator = DisasterOrchestrator()
        
        context = {
            "disaster_type": "fire",
            "location": "Test City",
            "severity": "moderate"
        }
        
        result = await orchestrator._call_llm_api(context)
        
        # Check that we got a response
        assert isinstance(result, dict)
        assert "summary" in result
        assert "overview" in result
        
        # If there's no error, we should have actual content
        if "Error" not in result["summary"]:
            assert len(result["overview"]) > 0
            print(f"\n✓ Real API test successful - Response length: {len(result['overview'])} chars")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])