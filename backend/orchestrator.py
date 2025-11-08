import aiohttp
import os
import json
from typing import Dict, Any


class DisasterOrchestrator:
    """
    Orchestrator that coordinates disaster response planning using LLM.
    """
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    def _log(self, message: str):
        """Log orchestrator activity"""
        print(f"[{self.name}] {message}")
    
    async def create_disaster(self, disaster_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new disaster response plan.
        This method will be expanded in future tasks.
        """
        self._log(f"Creating disaster response plan for: {disaster_data.get('type', 'Unknown')}")
        return {"status": "created", "id": "placeholder"}
    
    async def process_disaster(self, disaster_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process disaster and generate response plan using LLM.
        This method will be expanded in future tasks.
        """
        self._log(f"Processing disaster: {disaster_id}")
        
        # Call LLM API to generate plan
        plan = await self._call_llm_api(context)
        
        return plan
    
    async def _call_llm_api(self, context: Dict) -> Dict:
        """Call OpenRouter API to generate plan text"""
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            self._log("ERROR: OPENROUTER_API_KEY not set.")
            return {"summary": "Error: LLM API key not configured.", "overview": "", "templates": {}}

        # This prompt will be built in the next task
        prompt = self._build_master_prompt(context)
        
        self._log("Sending request to OpenRouter...")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    'https://openrouter.ai/api/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'anthropic/claude-3.5-sonnet',  # As specified in docs
                        'messages': [{'role': 'user', 'content': prompt}]
                    }
                ) as response:
                    if response.status != 200:
                        self._log(f"OpenRouter API Error: {response.status} {await response.text()}")
                        return {"summary": "Error: LLM API request failed.", "overview": "", "templates": {}}
                    
                    data = await response.json()
                    response_text = data['choices'][0]['message']['content']
                    
                    # This parsing logic will be built in a future task
                    return self._parse_llm_response(response_text)
                    
            except Exception as e:
                self._log(f"Error calling OpenRouter: {e}")
                return {"summary": "Error: LLM call exception.", "overview": "", "templates": {}}
    
    def _build_master_prompt(self, context: Dict) -> str:
        """
        Build the master prompt for the LLM.
        This method will be implemented in a future task.
        """
        self._log("Building master prompt (placeholder implementation)")
        return f"Generate a disaster response plan based on the following context: {json.dumps(context, indent=2)}"
    
    def _parse_llm_response(self, response_text: str) -> Dict:
        """
        Parse the LLM response into structured data.
        This method will be implemented in a future task.
        """
        self._log("Parsing LLM response (placeholder implementation)")
        return {
            "summary": "Plan generated successfully",
            "overview": response_text,
            "templates": {}
        }