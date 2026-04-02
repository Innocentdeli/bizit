from typing import Dict, Any, List

class PromptEngine:
    """
    Level 8: Generative Cognition.
    Structures agent reasoning as LLM-ready prompts.
    Even without a live LLM, this enforces 'Chain of Thought' architecture.
    """
    
    def construct_reasoning_prompt(self, agent_role: str, context: Dict[str, Any], goal: str) -> str:
        """
        Builds a structured prompt for decision making.
        Level 33: Multi-Objective Utility Alignment.
        """
        weights = context.get('utility_weights', {})
        weight_str = ", ".join([f"{k.capitalize()}: {v:.2f}" for k, v in weights.items()])
        
        prompt = f"""
        Role: {agent_role}
        Strategic Objective: {goal}
        
        Utility Weights (Priority Matrix): 
        [{weight_str}]
        
        Current Context:
        - Market Health (Weisman): {context.get('weisman_score', 0.5):.2f}
        - Available Budget: ${context.get('budget', 0):.2f} SOV
        - Metabolic Load (CPU): {context.get('metabolic_cpu', 10):.1f}%
        
        Recent Event:
        {context.get('event_summary', 'No recent events')}
        
        TASK:
        Propose the optimal action that maximizes utility across the 5 dimensions:
        1. Cashflow (Sales & Liquidity)
        2. Growth (Territory & Market Share)
        3. Efficiency (Resource usage & Speed)
        4. Fairness (Equitable agent workload)
        5. Resilience (Risk mitigation & Stability)

        OUTPUT FORMAT:
        {{
            "thought_process": "Analyze against the 5 dimensions, justifying the choice based on current weights.",
            "decision": "ACTION_NAME",
            "confidence": 0.0-1.0
        }}
        """
        return prompt.strip()

    async def generate_decision(self, agent_role: str, context: Dict[str, Any], goal: str, level: str = "STRATEGIC") -> Dict[str, Any]:
        """
        Level 60 Hackathon Edition: Calls Gemini 3 with Thinking Levels.
        """
        prompt = self.construct_reasoning_prompt(agent_role, context, goal)
        
        from core.config import ConfigLoader
        config = ConfigLoader(config_path="c:/bizit/config.yaml")
        
        if config.get("gemini.enabled", False):
            from cognitive_kernel.gemini_client import GeminiClient
            client = GeminiClient(
                api_key=config.get("gemini.api_key"),
                model_name=config.get("gemini.model", "gemini-3-pro-preview")
            )
            system_instr = f"You are {agent_role}, a sovereign BIZIT orchestrator. Output Thought Process + JSON Decision."
            return await client.generate_reasoning(prompt, system_instruction=system_instr, thinking_level=level)
        
        return self.mock_inference(prompt)

    def mock_inference(self, prompt: str) -> Dict[str, Any]:
        """
        Simulates an LLM response based on the prompt content.
        """
        # ... existing logic ...
