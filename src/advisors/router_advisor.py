from .base_advisor import BaseAgent
from ..models import RouterDecision, AdvisorType
from typing import Dict, Any

class RouterAgent(BaseAgent):
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        super().__init__("travel_router", ollama_host)
    
    def get_advisor_type(self) -> str:
        return "router"
    
    async def route_request(self, prompt: str, context: Dict[str, Any] = None) -> RouterDecision:
        """Route a travel request to the appropriate specialist advisor"""
        response = await self.process(prompt, context)
        
        if "error" in response:
            # Default routing on error
            return RouterDecision(
                advisor=AdvisorType.FLIGHT,  # Default fallback
                confidence=0.5,
                reasoning="Error in routing, defaulting to flight advisor",
                extracted_info={}
            )
        
        try:
            return RouterDecision(
                advisor=AdvisorType(response.get("advisor", response.get("agent", "flight"))),
                confidence=response.get("confidence", 0.5),
                reasoning=response.get("reasoning", ""),
                extracted_info=response.get("extracted_info", {})
            )
        except (ValueError, KeyError) as e:
            self.logger.warning("Invalid routing response", error=str(e), response=response)
            return RouterDecision(
                advisor=AdvisorType.FLIGHT,
                confidence=0.3,
                reasoning=f"Parsing error: {str(e)}",
                extracted_info={}
            )