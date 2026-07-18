import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .orchestrator import TravelOrchestrator
from .models import TravelRequest, AdvisorResponse
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

app = FastAPI(
    title="Multi-Advisor Travel Agency API",
    description="A specialized AI travel agency with flight, hotel, and car rental advisors",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = TravelOrchestrator(
    ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379")
)

@app.post("/travel/request", response_model=AdvisorResponse)
async def process_travel_request(request: TravelRequest):
    """Process a travel request through the appropriate specialist advisor"""
    try:
        response = await orchestrator.process_request(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/travel/session/{session_id}/context")
async def get_session_context(session_id: str):
    """Retrieve the context for a specific session"""
    context = await orchestrator.get_context(session_id)
    return {"session_id": session_id, "context": context}

@app.post("/travel/chat")
async def chat_endpoint(message: str, user_id: str = "anonymous", session_id: str = None):
    """Simple chat endpoint for testing"""
    if not session_id:
        session_id = str(uuid.uuid4())
    
    request = TravelRequest(
        message=message,
        user_id=user_id,
        session_id=session_id,
        context={}
    )
    
    response = await orchestrator.process_request(request)
    return {
        "session_id": session_id,
        "advisor": response.advisor.value,
        "response": response.response,
        "confidence": response.confidence
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return await orchestrator.health_check()

@app.get("/")
async def root():
    return {
        "message": "Multi-Advisor Travel Agency API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/travel/chat",
            "request": "/travel/request", 
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)