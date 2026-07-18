# Building a Multi-Advisor Travel Agency System with Ollama and Python

## How to Create Specialized AI Advisors That Work Together Using a Single Model Server

*Imagine having a team of AI specialists working together to handle complex travel bookings — each expert in their domain, yet seamlessly coordinating to deliver exceptional customer service. Today, we'll build exactly that using Ollama and Python.*

---

## The Challenge: Beyond Single-Purpose Chatbots

Most AI implementations today rely on monolithic models trying to be good at everything. But what if we could create a system where specialized AI advisors collaborate, each excelling in their specific domain? 

In this tutorial, we'll build a travel agency system with four specialized advisors:
- **Router Advisor**: Analyzes requests and routes them to the right specialist
- **Flight Advisor**: Handles flight bookings and searches
- **Hotel Advisor**: Manages hotel reservations
- **Car Rental Advisor**: Processes car rental requests

The magic? All running on a single Ollama instance, demonstrating how to build scalable, maintainable AI systems without the overhead of multiple model servers.

## Architecture Overview

Our system uses a hub-and-spoke model where one Ollama service hosts multiple fine-tuned models:

```
┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │     Redis       │
│   Orchestrator  │────│  Message Bus    │
└─────────────────┘    └─────────────────┘
         │                       │
    ┌────▼────────────────────────▼───┐
    │        Ollama Service           │
    │    (Single Instance)            │
    ├─────────────────────────────────┤
    │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ │
    │  │Router│ │Flight│ │Hotel│ │ Car │ │
    │  │Adv.  │ │Adv.  │ │Adv.  │ │Adv.  │ │
    │  └─────┘ └─────┘ └─────┘ └─────┘ │
    └─────────────────────────────────┘
```

## Project Structure

The complete system is organized as follows:

```
travel-agent/
├── docker-compose.yml       # Orchestrates Ollama, Redis, and API services
├── Dockerfile              # Container for the Python API
├── requirements.txt         # Python dependencies
├── setup_models.sh         # Script to initialize Ollama models
├── model/             # Ollama model configurations
│   ├── router.modelfile    # Router advisor specialization
│   ├── flight.modelfile    # Flight booking advisor
│   ├── hotel.modelfile     # Hotel reservation advisor
│   └── car.modelfile       # Car rental advisor
└── src/                    # Python application source
    ├── __init__.py
    ├── models.py           # Pydantic data models
    ├── orchestrator.py     # Coordinates advisor interactions
    ├── main.py            # FastAPI application
    └── agents/            # Individual advisor implementations
        ├── __init__.py
        ├── base_agent.py  # Base class for all advisors
        ├── router_agent.py # Routes requests to specialists
        ├── flight_agent.py # Flight booking logic
        ├── hotel_agent.py  # Hotel reservation logic
        └── car_agent.py    # Car rental logic
```

## Key Components

### Model Configuration Files
Each advisor is defined by a specialized Ollama Modelfile that configures:
- **Base model**: All advisors start from `llama2:7b`
- **System prompts**: Define the advisor's role and response format
- **Parameters**: Temperature, top_p for consistent behavior
- **Templates**: Structure how prompts are formatted

The router advisor is configured to return JSON routing decisions, while specialist advisors return structured responses for their domains.

### Python Implementation

**Data Models (`src/models.py`)**
- `AgentType`: Enum defining available advisor types
- `TravelRequest`: Input model for travel requests
- `AgentResponse`: Structured response from advisors
- `RouterDecision`: Routing logic output

**Base Advisor (`src/agents/base_agent.py`)**
- Abstract base class for all advisors
- Handles Ollama client communication with async support
- Provides JSON parsing with fallback to plain text
- Includes error handling and logging

**Specialist Advisors**
- Each advisor extends the base class with domain-specific methods
- Router advisor includes routing logic with fallback handling
- Service advisors (flight, hotel, car) have search and booking methods
- All advisors use the same async processing pattern

**Orchestrator (`src/orchestrator.py`)**
- Coordinates the entire multi-advisor workflow
- Uses async Redis for session context storage
- Routes requests through the router advisor
- Processes responses through specialist advisors
- Includes health checks for all advisors

**FastAPI Application (`src/main.py`)**
- RESTful API with three main endpoints:
  - `/travel/request`: Full request processing
  - `/travel/chat`: Simple chat interface
  - `/health`: System health monitoring
- Structured logging with JSON output
- CORS middleware for web integration

## Docker Configuration

The system uses Docker Compose to orchestrate three services:

1. **Ollama Service**: Hosts all AI models with memory limits and parallel processing
2. **Redis**: Provides session storage and message passing
3. **Travel API**: Python FastAPI application with hot-reload support

The configuration includes volume mounts for model persistence and development efficiency.

## Setup and Deployment

### Quick Start
```bash
# 1. Start all services
docker-compose up -d

# 2. Initialize the AI models
chmod +x setup_models.sh
./setup_models.sh

# 3. Test the system
curl -X POST "http://localhost:8000/travel/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a flight from NYC to London"}'
```

### Model Setup Process
The setup script handles:
- Waiting for Ollama service availability
- Pulling the base `llama2:7b` model
- Creating specialized models from Model
- Warming up models with test requests
- Verifying all agents are operational

## Example Interactions

**Simple Chat Request:**
```bash
curl -X POST "http://localhost:8000/travel/chat" \
  -d '{"message": "Book a hotel in Paris for December"}'
```

**Complex Request with Context:**
```bash
curl -X POST "http://localhost:8000/travel/request" \
  -d '{
    "message": "I need accommodation in Barcelona",
    "user_id": "user123",
    "session_id": "session456", 
    "context": {"budget": "mid-range", "travelers": 2}
  }'
```

The system automatically:
1. Routes the hotel request to the hotel advisor
2. Processes the request with budget and traveler context
3. Returns structured hotel recommendations
4. Stores session context for follow-up requests

## Key Benefits

1. **Specialization**: Each advisor excels in its domain rather than being mediocre at everything
2. **Efficiency**: Single Ollama instance handles multiple models without overhead
3. **Scalability**: Easy to add new agents or modify existing ones
4. **Maintainability**: Clear separation of concerns and modular design
5. **Cost-Effective**: No need for multiple model servers or API subscriptions

## Production Considerations

**Performance Optimization:**
- Model preloading and warm-up strategies
- Response caching for common requests
- Connection pooling for Redis and Ollama

**Monitoring & Observability:**
- Structured logging with request tracking
- Health checks for all system components
- Response time and success rate metrics

**Security & Reliability:**
- Input validation and sanitization
- Rate limiting and authentication
- Circuit breakers for graceful degradation
- Secrets management for configurations

## Conclusion

This multi-advisor travel system demonstrates how to build sophisticated AI applications using specialized advisors that collaborate effectively. By leveraging a single Ollama instance with multiple fine-tuned models, we achieve the benefits of specialization without operational complexity.

The architecture pattern applies beyond travel to any domain requiring specialized AI capabilities - customer service, e-commerce, healthcare, and more. The key is identifying distinct specializations and designing advisors that work together intelligently.

Ready to build your own multi-advisor system? The complete implementation is available in this repository - just clone, configure, and customize for your use case!#   t r a v e l _ a g e n c y _ s y s t e m  
 #   t r a v e l _ a g e n c y _ s y s t e m  
 #   t r a v e l _ a g e n c y _ s y s t e m  
 #   t r a v e l _ a g e n c y _ s y s t e m  
 