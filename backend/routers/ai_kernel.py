from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from cognitive_kernel.gemini_client import GeminiClient

router = APIRouter()
# Initialize Client (simulated singleton)
client = GeminiClient(model_name="gemini-2.5-flash")

class ChatRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

@router.post("/chat/completion")
async def ai_chat(request: ChatRequest):
    """
    Module 17: AI Augmentation Layer
    Proxies requests to the Co-Pilot / AI Agents.
    """
    if not client.api_key:
         return {
            "response": f"[MOCK] I analyzed your request '{request.query}'. (Configure GEMINI_API_KEY for real AI)",
            "actions": ["VIEW_MARKET_GAP"],
            "confidence": 0.85
        }

    # Contextual Prompting
    system_context = "You are Bizit Pulse, an advanced business intelligence AI. "
    if request.context:
        system_context += f"Current Context: {request.context}. "
    
    prompt = f"{system_context}\nUser Query: {request.query}\nProvide a concise, strategic response."
    
    try:
        response_text = await client.generate(prompt)
        return {
            "response": response_text,
            "actions": ["VIEW_DASHBOARD"], # Placeholder for action parsing
            "confidence": 0.95
        }
    except Exception as e:
        return {"response": "I encountered a cognitive error.", "error": str(e)}

@router.get("/insights/autosuggest")
async def get_autosuggestions(context: str = "general"):
    """
    Module 17: Proactive AI Suggestions
    """
    if not client.api_key:
        return {
            "suggestions": [
                f"Identify top {context} competitors",
                f"Analyze {context} pricing shifts",
                f"Scan for {context} supply gaps"
            ]
        }
        
    prompt = f"Generate 3 high-value, actionable business insights for a business in the '{context}' sector. Return as a JSON list of strings."
    
    try:
        # Use reasoning for structured JSON
        result = await client.generate_reasoning(
            prompt=prompt,
            thinking_level="TACTICAL"
        )
        # Assuming the reasoning engine returns a dict with 'suggestions' or similar
        # Based on gemini_client check
        if isinstance(result, dict) and "suggestions" in result:
             return {"suggestions": result["suggestions"]}
        
        return {
            "suggestions": [
                f"Optimize {context} delivery logistics",
                f"Evaluate {context} customer retention trends",
                f"Explore {context} digital expansion"
            ] 
        } 
    except Exception as e:
        return {"suggestions": ["Intelligence synthesis temporarily unavailable."]}
