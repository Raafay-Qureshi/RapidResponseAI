from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def analyze(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Main analysis method - must be implemented by each agent
        Returns a dictionary with analysis results
        """
        pass
    
    def _log(self, message: str):
        """Log agent activity"""
        print(f"[{self.name}] {message}")