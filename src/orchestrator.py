import redis.asyncio as redis
import json
import structlog
from typing import Dict, Any, Optional
from .advisors.router_advisor import RouterAgent
from .advisors.flight_advisor import FlightAgent
from .advisors.hotel_advisor import HotelAgent
from .advisors.car_advisor import CarAgent
from .models import TravelRequest, AdvisorResponse, AdvisorType

logger = structlog.get_logger()

class TravelOrchestrator:
    def __init__(self, ollama_host: str = "http://localhost:11434", redis_url: str = "redis://localhost:6379"):
        self.ollama_host = ollama_host
        self.redis_client = redis.from_url(redis_url)
        
        # Initialize advisors
        self.router = RouterAgent(ollama_host)
        self.advisors = {
            AdvisorType.FLIGHT: FlightAgent(ollama_host),
            AdvisorType.HOTEL: HotelAgent(ollama_host),
            AdvisorType.CAR: CarAgent(ollama_host)
        }
        
        self.logger = logger.bind(component="orchestrator")
    
    async def process_request(self, request: TravelRequest) -> AdvisorResponse:
        """Process a travel request through the appropriate advisor"""
        try:
            # Store request context in Redis
            await self._store_context(request.session_id, request.context)
            
            # Route the request
            routing_decision = await self.router.route_request(
                request.message, 
                request.context
            )
            
            self.logger.info(
                "Request routed",
                advisor=routing_decision.advisor.value,
                confidence=routing_decision.confidence,
                session_id=request.session_id
            )
            
            # Get advisor and process request
            advisor = self.advisors.get(routing_decision.advisor)
            if not advisor:
                raise ValueError(f"Unknown advisor type: {routing_decision.advisor}")
            
            # Add routing context to the request
            enhanced_context = {
                **request.context,
                "routing_info": routing_decision.extracted_info,
                "routing_confidence": routing_decision.confidence
            }
            
            # Process with the specialist advisor
            response = await advisor.process(request.message, enhanced_context)
            
            # Store response in session context
            await self._update_context(request.session_id, {
                "last_advisor": routing_decision.advisor.value,
                "last_response": response
            })
            
            return AdvisorResponse(
                advisor=routing_decision.advisor,
                response=response,
                confidence=routing_decision.confidence,
                processing_time=response.get("processing_time", 0),
                session_id=request.session_id
            )
            
        except Exception as e:
            self.logger.error("Error processing request", error=str(e), session_id=request.session_id)
            return AdvisorResponse(
                advisor=AdvisorType.FLIGHT,  # Default fallback
                response={"error": str(e), "message": "Sorry, I encountered an error processing your request."},
                confidence=0.0,
                processing_time=0.0,
                session_id=request.session_id
            )
    
    async def _store_context(self, session_id: str, context: Dict[str, Any]):
        """Store session context in Redis"""
        try:
            key = f"session:{session_id}"
            await self.redis_client.set(key, json.dumps(context), ex=3600)  # 1 hour expiry
        except Exception as e:
            self.logger.warning("Failed to store context", error=str(e))
    
    async def _update_context(self, session_id: str, updates: Dict[str, Any]):
        """Update session context in Redis"""
        try:
            key = f"session:{session_id}"
            existing = await self.redis_client.get(key)
            
            if existing:
                context = json.loads(existing)
                context.update(updates)
                await self.redis_client.set(key, json.dumps(context), ex=3600)
        except Exception as e:
            self.logger.warning("Failed to update context", error=str(e))
    
    async def get_context(self, session_id: str) -> Dict[str, Any]:
        """Retrieve session context from Redis"""
        try:
            key = f"session:{session_id}"
            context = await self.redis_client.get(key)
            return json.loads(context) if context else {}
        except Exception as e:
            self.logger.warning("Failed to retrieve context", error=str(e))
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all advisors"""
        health_status = {"status": "healthy", "advisors": {}}
        
        # Check router
        try:
            await self.router.process("health check", {})
            health_status["advisors"]["router"] = "healthy"
        except Exception as e:
            health_status["advisors"]["router"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
        
        # Check specialist advisors
        for advisor_type, advisor in self.advisors.items():
            try:
                await advisor.process("health check", {})
                health_status["advisors"][advisor_type.value] = "healthy"
            except Exception as e:
                health_status["advisors"][advisor_type.value] = f"unhealthy: {str(e)}"
                health_status["status"] = "degraded"
        
        return health_status