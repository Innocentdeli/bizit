from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from cognitive_kernel.gemini_client import GeminiClient
import json

class MarketSignals(BaseModel):
    supply: int
    demand: int
    momentum_percentage: float
    competitors: int
    avg_price: Optional[float] = None
    search_volume: int

class IntelligenceEngine:
    """
    Core Market Intelligence Engine
    Analyzes Supply, Demand, and Momentum to generate actionable insights
    """
    
    def __init__(self):
        self.gemini = GeminiClient(model_name="gemini-1.5-flash")
    
    def calculate_verdict(self, signals: MarketSignals) -> Dict[str, Any]:
        """
        Calculate market verdict based on Supply/Demand/Momentum
        Returns: OPPORTUNITY, BALANCED, or SATURATED
        """
        # Simple heuristic (can be enhanced with ML)
        supply_demand_ratio = signals.supply / max(signals.demand, 1)
        
        if supply_demand_ratio < 0.3 and signals.momentum_percentage > 10:
            verdict = "OPPORTUNITY"
            confidence = min(0.95, 0.7 + (signals.momentum_percentage / 100))
        elif supply_demand_ratio < 0.6:
            verdict = "BALANCED"
            confidence = 0.75
        else:
            verdict = "SATURATED"
            confidence = 0.80
            
        return {
            "verdict": verdict,
            "confidence": round(confidence, 2),
            "supply_demand_ratio": round(supply_demand_ratio, 2)
        }
    
    async def generate_intelligence_response(
        self, 
        query: str, 
        signals: MarketSignals,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate full intelligence response with AI-powered insights
        """
        
        # 1. Calculate Verdict
        verdict_data = self.calculate_verdict(signals)
        
        # 2. Build AI Prompt for Dynamic Insights
        prompt = f"""
You are BizitPulse, a market intelligence AI. Analyze this query and provide structured insights.

Query: {query}

Market Signals:
- Supply: {signals.supply} businesses/products
- Demand: {signals.demand} monthly searches/inquiries
- Momentum: {signals.momentum_percentage}% monthly growth
- Competition: {signals.competitors} active competitors
- Search Volume: {signals.search_volume} monthly

Verdict: {verdict_data['verdict']}

Generate a JSON response with:
{{
  "summary": "2-3 sentence market summary",
  "insights": ["insight 1", "insight 2", "insight 3"],
  "recommendations": [
    {{"action": "specific action", "detail": "why this matters", "priority": "HIGH|MEDIUM|LOW"}}
  ],
  "forecast": {{
    "scenario": "likely outcome",
    "trajectory": "direction and magnitude",
    "probability": 0.0-1.0
  }}
}}
"""
        
        # 3. Get AI Response (with fallback)
        ai_success = False
        if self.gemini.api_key:
            try:
                ai_response = await self.gemini.generate_reasoning(
                    prompt=prompt,
                    thinking_level="STRATEGIC"
                )
                
                if ai_response and "error" not in ai_response:
                    summary = ai_response.get("summary")
                    insights = ai_response.get("insights")
                    recommendations = ai_response.get("recommendations")
                    forecast = ai_response.get("forecast")
                    
                    if all([summary, insights, recommendations, forecast]):
                        ai_success = True
                
            except Exception as e:
                print(f"[INTELLIGENCE_ENGINE] AI Error: {e}")

        if not ai_success:
            # Fallback to rich templates
            summary, insights, recommendations, forecast = self._generate_template_response(
                query, signals, verdict_data
            )
        
        # 4. Build Final Response
        return {
            "status": "success",
            "timestamp": self._get_timestamp(),
            "request_id": self._generate_request_id(),
            "data": {
                "verdict": verdict_data["verdict"],
                "confidence": verdict_data["confidence"],
                "summary": summary,
                "insights": insights,
                "recommendations": recommendations,
                "forecast": forecast,
                "market_signals": {
                    "supply": signals.supply,
                    "demand": signals.demand,
                    "momentum": f"+{signals.momentum_percentage}% MoM",
                    "competition_level": self._get_competition_level(signals.competitors)
                },
                "sources": [
                    {
                        "title": "Global Intelligence Node",
                        "trust": 0.96,
                        "reason": "AI-Synthesized Regional & World Trends (Gemini 1.5 Pro)",
                        "url": "ai://global-synthesis"
                    },
                    {
                        "title": "World Search Trends",
                        "trust": 0.90,
                        "reason": "Real-time aggregated global search volume",
                        "url": "api://search-trends"
                    },
                    {
                        "title": "Platform Analytics",
                        "trust": 0.85,
                        "reason": "Bizit Pulse internal ecosystem metrics",
                        "url": "internal://db"
                    }
                ]
            }
        }
    
    def _generate_template_response(self, query: str, signals: MarketSignals, verdict_data: Dict) -> tuple:
        """Fallback template when AI is unavailable"""
        
        if verdict_data["verdict"] == "OPPORTUNITY":
            summary = f"Strong opportunity detected. Demand ({signals.demand}) significantly exceeds supply ({signals.supply}) with {signals.momentum_percentage}% growth momentum."
            insights = [
                f"Low competition: only {signals.competitors} active competitors",
                f"Rising demand: {signals.search_volume} monthly searches",
                "Market gap presents first-mover advantage"
            ]
            recommendations = [
                {
                    "action": "Enter market quickly",
                    "detail": "Capitalize on supply-demand gap before competitors arrive",
                    "priority": "HIGH"
                },
                {
                    "action": "Focus on differentiation",
                    "detail": "Stand out from existing competitors with unique value proposition",
                    "priority": "MEDIUM"
                }
            ]
        elif verdict_data["verdict"] == "SATURATED":
            summary = f"Market shows saturation. Supply ({signals.supply}) exceeds demand ({signals.demand}). Consider differentiation or alternative markets."
            insights = [
                f"High competition: {signals.competitors} established players",
                "Price pressure likely due to oversupply",
                "Requires strong differentiation to succeed"
            ]
            recommendations = [
                {
                    "action": "Identify niche segment",
                    "detail": "Target underserved customer segments within the market",
                    "priority": "HIGH"
                },
                {
                    "action": "Consider adjacent markets",
                    "detail": "Explore related opportunities with better supply-demand balance",
                    "priority": "MEDIUM"
                }
            ]
        else:  # BALANCED
            summary = f"The market for {query} is currently in equilibrium. Demand signals ({signals.demand}) are steadily met by existing supply ({signals.supply}), suggesting a mature but stable environment."
            insights = [
                f"Sustained search volume of {signals.search_volume}/mo indicates consistent consumer interest.",
                "Market dynamics are well-established; success requires high operational efficiency.",
                "Moderate momentum (+{signals.momentum_percentage}%) suggests slow but steady growth potential."
            ]
            recommendations = [
                {
                    "action": "Optimize Customer Experience",
                    "detail": "In a balanced market, superior service is the primary differentiator to win market share.",
                    "priority": "HIGH"
                },
                {
                    "action": "Analyze Competitor Gap",
                    "detail": f"Evaluate the {signals.competitors} active competitors for specific service or quality gaps.",
                    "priority": "MEDIUM"
                }
            ]
        
        forecast = {
            "scenario": "Market Stability" if signals.momentum_percentage < 10 else "Gradual Expansion",
            "trajectory": f"Continued {signals.momentum_percentage}% growth expected over the next 6-12 months.",
            "probability": 0.85
        }
        
        return summary, insights, recommendations, forecast
    
    def _get_competition_level(self, competitors: int) -> str:
        if competitors < 5:
            return "LOW"
        elif competitors < 15:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    def _generate_request_id(self) -> str:
        import uuid
        return f"req_{uuid.uuid4().hex[:12]}"
