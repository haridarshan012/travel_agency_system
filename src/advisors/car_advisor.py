from .base_advisor import BaseAgent
from typing import Dict, Any

class CarAgent(BaseAgent):
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        super().__init__("travel_car", ollama_host)
    
    def get_advisor_type(self) -> str:
        return "car"
    
    async def search_rentals(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search for car rentals based on user request"""
        enhanced_prompt = f"""
        Car Rental Search Request: {request}
        
        Please provide rental options with:
        - Available vehicles with specifications and prices
        - Pickup/dropoff locations and times
        - Insurance and additional options
        - Rental terms and conditions
        """
        
        return await self.process(enhanced_prompt, context)
    
    async def book_rental(self, booking_details: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process car rental booking request"""
        prompt = f"""
        Car Rental Booking Request:
        Details: {booking_details}
        
        Process this rental and provide:
        - Rental agreement details
        - Driver requirements and documentation
        - Pickup procedures
        - Return policies
        """
        
        return await self.process(prompt, context)