from .base_advisor import BaseAgent
from typing import Dict, Any

class HotelAgent(BaseAgent):
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        super().__init__("travel_hotel", ollama_host)
    
    def get_advisor_type(self) -> str:
        return "hotel"
    
    async def search_hotels(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search for hotels based on user request"""
        enhanced_prompt = f"""
        Hotel Search Request: {request}
        
        Please provide hotel recommendations with:
        - Available properties with ratings and prices
        - Room types and amenities
        - Location benefits
        - Booking conditions and cancellation policies
        """
        
        return await self.process(enhanced_prompt, context)
    
    async def book_hotel(self, booking_details: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process hotel booking request"""
        prompt = f"""
        Hotel Booking Request:
        Details: {booking_details}
        
        Process this reservation and provide:
        - Reservation confirmation
        - Check-in/check-out procedures
        - Hotel policies and amenities
        - Contact information
        """
        
        return await self.process(prompt, context)