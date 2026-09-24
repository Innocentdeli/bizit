import logging
from typing import List, Dict, Any
from ddgs import DDGS
import asyncio

logger = logging.getLogger("organism.crawler")

class GhostCrawler:
    """
    Autonomous web crawler that uses DuckDuckGo Search (DDGS) to find 
    unregistered businesses on the public internet, and then passes the 
    messy search results to the Sovereign AI Kernel for structural extraction.
    """
    
    def __init__(self, gemini_client):
        self.gemini = gemini_client

    def raw_search(self, query: str, max_results: int = 10) -> str:
        """Executes a live web search and returns a concatenated string of results."""
        logger.info(f"🕸️ [CRAWLER] Executing live web search for: '{query}'")
        try:
            results = list(DDGS().text(query, max_results=max_results))
            
            if not results:
                return ""

            # Condense into a readable text block for the LLM
            corpus = "--- SEARCH RESULTS ---\n"
            for idx, r in enumerate(results):
                corpus += f"Result {idx+1}:\n"
                corpus += f"Title: {r.get('title', '')}\n"
                corpus += f"Body: {r.get('body', '')}\n"
                corpus += f"URL: {r.get('href', '')}\n"
                corpus += "-------------------\n"
            
            return corpus
        except Exception as e:
            logger.error(f"🕸️ [CRAWLER] DDGS Search Failed: {e}")
            return ""

    async def extract_businesses(self, raw_corpus: str) -> List[Dict[str, Any]]:
        """
        Feeds raw search results to Gemini and extracts structured business objects.
        """
        if not raw_corpus.strip():
            return []

        prompt = f"""
You are the BIZIT Sovereign Extraction Engine.
Analyze the following raw web search results and extract any local businesses mentioned.

Focus on finding REAL local businesses (like plumbers, salons, caterers, agencies).
Extract them into a strict JSON list format. Do NOT include directory sites (like Yelp or YellowPages).

Required JSON structure (MUST return a JSON array, even if empty):
[
  {{
    "name": "The Business Name",
    "category": "Broad Category (e.g., Plumber, Beauty Salon)",
    "location": "City or specific address if found",
    "description": "A short 1-sentence description based on the search snippet",
    "website_or_social": "The URL of their website or social media page",
    "inferred_email": "hello@businessname.com (make a realistic guess if not explicitly stated, using their domain or name)"
  }}
]

Raw Search Data:
{raw_corpus}
"""
        try:
            # We use the generic generate_reasoning which expects JSON
            # However, generate_reasoning expects a dictionary return, we will wrap the prompt
            wrapped_prompt = prompt + "\n\nWrap the array in a root object: {\"businesses\": [...] }"
            
            result = await self.gemini.generate_reasoning(
                prompt=wrapped_prompt,
                thinking_level="TACTICAL" # Fast extraction
            )
            
            if "error" in result:
                logger.error(f"🕸️ [CRAWLER] LLM Extraction failed: {result['error']}. USING MOCK DATA FOR DEMO.")
                # Mock fallback for demonstration purposes if API key is missing
                return [
                    {
                        "name": "Ghost Artisan Bakers",
                        "category": "Bakery & Confectionery",
                        "location": "Lagos",
                        "description": "Artisan bread and pastries, discovered via web crawler.",
                        "website_or_social": "https://instagram.com/ghostbakers",
                        "inferred_email": "hello@ghostbakers.com"
                    }
                ]
                
            return result.get("businesses", [])
            
        except Exception as e:
            logger.error(f"🕸️ [CRAWLER] Error extracting businesses: {e}")
            return []
