from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

class AdvisorType(str, Enum):
    ROUTER = "router"
    FLIGHT = "flight"
    HOTEL = "hotel"
    CAR = "car"

class TravelRequest(BaseModel):
    message: str
    user_id: str
    session_id: str
    context: Optional[Dict[str, Any]] = {}

class AdvisorResponse(BaseModel):
    advisor: AdvisorType
    response: Dict[str, Any]
    confidence: float
    processing_time: float
    session_id: str

class RouterDecision(BaseModel):
    advisor: AdvisorType
    confidence: float
    reasoning: str
    extracted_info: Dict[str, Any]