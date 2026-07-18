from .base_advisor import BaseAgent
from typing import Dict, Any

class FlightAgent(BaseAgent):
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        super().__init__("travel_flight", ollama_host)
    
    def get_advisor_type(self) -> str:
        return "flight"
    
    async def search_flights(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search for flights based on user request"""
        enhanced_prompt = f"""
        Flight Search Request: {request}
        
        Please provide flight options with the following information:
        - Available flights with times and prices
        - Airline recommendations
        - Alternative dates if beneficial
        - Booking next steps
        """
        
        return await self.process(enhanced_prompt, context)
    
    async def book_flight(self, booking_details: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process flight booking request"""
        prompt = f"""
        Flight Booking Request:
        Details: {booking_details}
        
        Process this booking and provide:
        - Booking confirmation steps
        - Required passenger information
        - Payment processing
        - Booking reference details
        """
        
        return await self.process(prompt, context)