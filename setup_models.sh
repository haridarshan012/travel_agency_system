#!/bin/bash

echo "Setting up Travel Agency AI Models..."

# Wait for Ollama to be ready
echo "Waiting for Ollama service..."
while ! curl -f http://localhost:11434/api/version > /dev/null 2>&1; do
    sleep 2
done

echo "Ollama is ready! Creating specialized models..."

# Pull base model
echo "Pulling base model..."
ollama pull llama2:7b

# Create specialized models
echo "Creating router advisor..."
ollama create travel_router -f ./model/router.modelfile

echo "Creating flight advisor..."
ollama create travel_flight -f ./model/flight.modelfile

echo "Creating hotel advisor..."  
ollama create travel_hotel -f ./model/hotel.modelfile

echo "Creating car rental advisor..."
ollama create travel_car -f ./model/car.modelfile

# Warm up models
echo "Warming up models..."
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "travel_router", "prompt": "test", "options": {"num_predict": 1}}' > /dev/null

curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "travel_flight", "prompt": "test", "options": {"num_predict": 1}}' > /dev/null

curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "travel_hotel", "prompt": "test", "options": {"num_predict": 1}}' > /dev/null

curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "travel_car", "prompt": "test", "options": {"num_predict": 1}}' > /dev/null

echo "✅ All models are ready!"
echo "You can now test the API at http://localhost:8000"