import httpx
import json
import logging
from typing import AsyncGenerator, Dict, Any, Optional

logger = logging.getLogger(__name__)

class LocalLLMClient:
    """
    Client for communicating with a local Ollama instance.
    Implements the Cognitive Core interface with Asynchronous support.
    """
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        import os
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2:latest")
        self.generate_endpoint = f"{self.base_url}/api/generate"
        self.timeout = httpx.Timeout(60.0, connect=5.0)
        logger.info(f"🧠 Async Local LLM Client initialized (Model: {self.model}, URL: {self.base_url})")

    async def generate_stream(self, prompt: str, system: Optional[str] = None) -> AsyncGenerator[str, None]:
        """
        Generates a streaming response from the local model.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", self.generate_endpoint, json=payload) as response:
                    if response.status_code != 200:
                        yield f"Error: {await response.aread()}"
                        return

                    async for line in response.aiter_lines():
                        if line:
                            try:
                                json_response = json.loads(line)
                                chunk = json_response.get("response", "")
                                if chunk:
                                    yield chunk
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"LLM Streaming Error: {e}")
            yield f"⚠️ [SYNAPSE_FAILURE] Connection to Ollama failed: {str(e)}"

    async def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Generates a blocking (but async) response from the local model.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.generate_endpoint, json=payload)
                if response.status_code != 200:
                    return f"Error: {response.text}"
                return response.json().get("response", "")
        except Exception as e:
            logger.error(f"LLM Generation Error: {e}")
            return f"⚠️ [COGNITIVE_CORE_OFFLINE]: {str(e)}"
