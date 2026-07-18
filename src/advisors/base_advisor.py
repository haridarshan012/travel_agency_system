import ollama
import json
import time
import asyncio
import structlog
from abc import ABC, abstractmethod
from typing import Dict, Any

logger = structlog.get_logger()

class BaseAgent(ABC):
    def __init__(self, model_name: str, ollama_host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.client = ollama.Client(host=ollama_host)
        self.logger = logger.bind(advisor=self.model_name)
    
    async def process(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a request and return structured response"""
        start_time = time.time()
        
        try:
            # Prepare the full prompt with context
            full_prompt = self._prepare_prompt(prompt, context or {})
            
            # Generate response
            response = await self._generate_response(full_prompt)
            
            # Parse and validate response
            parsed_response = self._parse_response(response)
            
            processing_time = time.time() - start_time
            
            self.logger.info(
                "Request processed successfully",
                processing_time=processing_time,
                prompt_length=len(prompt)
            )
            
            return {
                **parsed_response,
                "processing_time": processing_time,
                "advisor": self.model_name
            }
            
        except Exception as e:
            self.logger.error("Error processing request", error=str(e))
            return {
                "error": str(e),
                "advisor": self.model_name,
                "processing_time": time.time() - start_time
            }
    
    async def _generate_response(self, prompt: str) -> str:
        """Generate response using Ollama"""
        try:
            # Run synchronous Ollama client in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.generate(
                    model=self.model_name,
                    prompt=prompt,
                    stream=False
                )
            )
            return response['response']
        except Exception as e:
            self.logger.error("Ollama generation failed", error=str(e))
            raise
    
    def _prepare_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Prepare the prompt with context information"""
        if not context:
            return prompt
        
        context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
        return f"Context:\n{context_str}\n\nRequest: {prompt}"
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the model response into structured format"""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback to plain text response
                return {"message": response.strip(), "format": "text"}
                
        except json.JSONDecodeError:
            return {"message": response.strip(), "format": "text"}
    
    @abstractmethod
    def get_advisor_type(self) -> str:
        """Return the advisor type identifier"""
        pass