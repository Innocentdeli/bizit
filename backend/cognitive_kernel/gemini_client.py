import httpx
import os
import json
import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class GeminiClient:
    """
    Sovereign Cognitive Engine powered by Gemini 1.5.
    Direct API implementation using httpx (SDK Fallback).
    """
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        if not self.api_key:
            logger.warning("âš ï¸ [GEMINI] No API Key found. Client will operate in MOCK mode.")
        else:
            logger.info(f"âœ… [GEMINI] Sovereign AI online. Model: {self.model_name}")


    async def generate(self, prompt: str) -> str:
        """Lightweight text generation for tactical tasks."""
        if not self.api_key:
            return "MACRO, RISK, FORECAST" # Mock fallback
            
        url = f"{self.base_url}/{self.model_name}:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generation_config": {
                "temperature": 0.2,
                "max_output_tokens": 1024,
            },
            "safety_settings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code != 200:
                    logger.error(f"Gemini API Error {response.status_code}: {response.text}")
                    return ""
                data = response.json()
                try:
                    candidate = data['candidates'][0]
                    if candidate.get('finishReason') != 'STOP' and candidate.get('finishReason') is not None:
                        logger.warning(f"Gemini Finish Reason: {candidate.get('finishReason')}")
                    
                    return candidate['content']['parts'][0]['text'].strip()
                except (KeyError, IndexError):
                    logger.error(f"Gemini Unexpected Response Structure: {json.dumps(data)}")
                    return ""
        except Exception as e:
            logger.error(f"Gemini Request Exception: {e}")
            return ""
        
    async def generate_multimodal(self, prompt: str, data_bytes: bytes, mime_type: str = "image/jpeg") -> str:
        """Multimodal generation for visual and audio intelligence."""
        if not self.api_key:
            return "MULTIMODAL_SIGNAL_MOCK: Extracted strategic intelligence."
            
        url = f"{self.base_url}/{self.model_name}:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        
        import base64
        encoded_data = base64.b64encode(data_bytes).decode('utf-8')
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": encoded_data
                        }
                    }
                ]
            }],
            "generation_config": {
                "temperature": 0.2,
                "max_output_tokens": 2048,
            },
            "safety_settings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code != 200:
                    logger.error(f"Gemini Multimodal Error: {response.text}")
                    return ""
                data = response.json()
                try:
                    candidate = data['candidates'][0]
                    if candidate.get('finishReason') != 'STOP' and candidate.get('finishReason') is not None:
                        logger.warning(f"Gemini Multimodal Finish Reason: {candidate.get('finishReason')}")
                    
                    return candidate['content']['parts'][0]['text'].strip()
                except (KeyError, IndexError):
                    logger.error(f"Gemini Multimodal Unexpected Response: {json.dumps(data)}")
                    return ""
        except Exception as e:
            logger.error(f"Gemini Multimodal Exception: {e}")
            return ""

    async def generate_reasoning(self, prompt: str, system_instruction: Optional[str] = None, thinking_level: str = "STRATEGIC") -> Dict[str, Any]:
        """
        Calls Gemini 2.5 Pro via REST API.
        Level 60 Sovereign Intelligence Logic.
        """
        if not self.api_key:
            logger.error("âŒ [GEMINI] API Key missing. Aborting reasoning synthesis.")
            return {"error": "GEMINI_API_KEY is missing. High-fidelity synthesis is unavailable."}
            
        # Dynamic Quota Fallback Logic
        models_to_try = [self.model_name, "gemini-2.5-flash", "gemini-2.5-flash"]
        # Remove duplicates while keeping order
        models_to_try = list(dict.fromkeys(models_to_try))

        for attempt_model in models_to_try:
            url = f"{self.base_url}/{attempt_model}:generateContent?key={self.api_key}"
            
            headers = {'Content-Type': 'application/json'}
            
            # Thinking Level Modifiers
            temp = 0.2 if thinking_level == "TACTICAL" else 0.7
            thought_prefix = "[SOVEREIGN_REASONING_MODE]\nAnalyze this query with multi-step strategic foresight.\n\n"

            payload = {
                "contents": [{
                    "parts": [{"text": thought_prefix + prompt}]
                }],
                "generation_config": {
                    "temperature": temp,
                    "max_output_tokens": 4096 if thinking_level == "SOVEREIGN" else 2048,
                    "response_mime_type": "application/json",
                }
            }
            
            system_base = "You are BIZIT Pulse, the Sovereign Intelligence Engine. "
            system_base += "Provide deep market intelligence. Output VALID JSON ONLY."
            
            payload["system_instruction"] = {
                "parts": [{"text": f"{system_base} {system_instruction or ''}"}]
            }

            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(url, headers=headers, json=payload)
                    
                    if response.status_code == 429:
                        logger.warning(f"âš ï¸ [GEMINI] Rate limit hit on {attempt_model}. Trying next fallback model...")
                        continue # Try the next model
                        
                    if response.status_code != 200:
                        logger.error(f"Gemini API Error {response.status_code} on {attempt_model}: {response.text}")
                        return {"error": f"API Error {response.status_code}", "details": response.text}

                
                data = response.json()
                try:
                    text_response = data['candidates'][0]['content']['parts'][0]['text']
                    
                    # Robust cleaning and parsing
                    import re
                    # Look for everything between the first '{' and the last '}' (if it exists)
                    # if not, take from the first '{' to the end
                    first_brace = text_response.find('{')
                    if first_brace == -1:
                        raise ValueError("No JSON object found in response")
                    
                    last_brace = text_response.rfind('}')
                    if last_brace != -1 and last_brace > first_brace:
                        cleaned_text = text_response[first_brace:last_brace+1]
                    else:
                        cleaned_text = text_response[first_brace:]

                    # Repair common truncation issues
                    cleaned_text = self._repair_json(cleaned_text)

                    try:
                        decision_data = json.loads(cleaned_text)
                    except json.JSONDecodeError as je:
                        logger.error(f"JSON Parse Error even after repair: {je}")
                        # Final attempt: just return error if unrecoverable
                        raise
                        
                    # Add Thought Signature
                    decision_data["thought_signature"] = {
                        "level": thinking_level,
                        "model": self.model_name,
                        "trace_id": os.urandom(4).hex()
                    }
                    return decision_data
                except (KeyError, IndexError, json.JSONDecodeError, TypeError, ValueError) as e:
                    logger.error(f"Failed to parse Gemini response: {e}")
                    return {
                        "error": "Synthesis Parsing Failed",
                        "message": str(e),
                        "status": "SCHEMA_MISMATCH"
                    }
            
            except Exception as e:
                logger.error(f"Gemini Request Error: {e}")
                # We do not return immediately on network errors either, just in case a fallback model works
                logger.warning(f"âš ï¸ [GEMINI] Network/Request Error on {attempt_model}. Trying next fallback model...")
                continue
                
        # If the loop completes without returning, all models failed (likely 429 Quota Exceeded on all)
        logger.error("âŒ [GEMINI] All fallback models exhausted. Rate limits or network failures across the board.")
        return {"error": "All fallback models exhausted due to rate limits or network errors.", "status": "RESOURCE_EXHAUSTED"}

    def _repair_json(self, json_str: str) -> str:
        """Helper to repair common truncation/malformation in LLM JSON outputs."""
        # 1. Strip whitespace
        s = json_str.strip()
        
        # 2. Handle unterminated strings at the end
        # If the string ends inside a value e.g. "foo": "bar
        if s.count('"') % 2 != 0:
            s += '"'
            
        # 3. Remove trailing commas before closing braces/brackets
        s = re.sub(r',\s*([\]\}])', r'\1', s)
        
        # 4. Balance braces
        open_braces = s.count('{')
        close_braces = s.count('}')
        if open_braces > close_braces:
            s += '}' * (open_braces - close_braces)
        
        return s
