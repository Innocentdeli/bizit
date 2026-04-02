from cognitive_kernel.tool_registry import AgentTool
from typing import Dict, Any
import logging
import os
import json

logger = logging.getLogger(__name__)

class WebSearchTool(AgentTool):
    """
    allows agents to search the web for information.
    Uses Serper.dev (Google Search API) for real-time results.
    """
    def __init__(self):
        super().__init__("web_search", "Search the internet for real-time information.")
        self.api_key = os.getenv("SERPER_API_KEY", "")

    def execute(self, query: str = "", **kwargs) -> Dict[str, Any]:
        logger.info(f"🔍 [WEB_SEARCH] Searching for: '{query}'")
        
        if not self.api_key:
            logger.error("❌ [WEB_SEARCH] SERPER_API_KEY is missing. Aborting search.")
            return {
                "status": "error",
                "message": "SERPER_API_KEY is missing. Real-time intelligence gathering requires a valid API key."
            }
            
        try:
            url = "https://google.serper.dev/search"
            payload = json.dumps({"q": query})
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            # Using standard requests (synchronous for now, or could use httpx if preferred)
            # Since agents run in threads/processes, sync requests are usually fine, 
            # but usually we prefer async. BaseAgent isn't fully async yet.
            import requests
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Parse Organic Results
                for item in data.get("organic", [])[:10]:
                    results.append({
                        "title": item.get("title"),
                        "snippet": item.get("snippet"),
                        "link": item.get("link")
                    })
                    
                # Parse Knowledge Graph if available
                if "knowledgeGraph" in data:
                    kg = data["knowledgeGraph"]
                    results.insert(0, {
                        "title": kg.get("title"),
                        "snippet": kg.get("description"),
                        "link": kg.get("website")
                    })
                    
                return {
                    "status": "success",
                    "query": query,
                    "results": results,
                    "provider": "serper.dev"
                }
            else:
                return {
                    "status": "error", 
                    "message": f"Search API failed: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Search Execution Failed: {e}")
            return {"status": "error", "message": str(e)}

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "name": "web_search",
            "description": "Search the web for a given query string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."}
                },
                "required": ["query"]
            }
        }
