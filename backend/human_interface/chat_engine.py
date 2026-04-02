import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator
from event_graph.graph_manager import GraphManager
from core.state import OrganismState
from cognitive_kernel.local_llm_client import LocalLLMClient
from cognitive_kernel.digital_twin import DigitalTwin

logger = logging.getLogger(__name__)

class ChatEngine:
    """
    Implements USER INTERFACE 2: CHAT INTERFACE via Local Sovereign AI.
    Asynchronous version with streaming support and optimized RAG.
    """
    
    def __init__(self, graph_manager: GraphManager, state: OrganismState):
        self.graph = graph_manager
        self.state = state
        self.llm = LocalLLMClient()
        self.twin = DigitalTwin(state)
        logger.info("Async ChatEngine awakened with Ancestral Memory and Streaming Synapses.")

    async def handle_message_async(self, data: dict) -> AsyncGenerator[str, None]:
        """
        Asynchronous message handler returning a stream of tokens.
        Includes Level 35b: Sovereign Actuation (Intent Recognition).
        """
        query = data.get("query") or data.get("message") or ""
        
        # --- Level 35b: Sovereign Actuation (Intent Parsing) ---
        # Very simple keyword-based intent for now. 
        # In Level 40, this becomes a proper NLP classifier or function calling.
        
        lower_query = query.lower()
        tool_triggered = False
        target_agent = None
        tool_name = None
        tool_args = {}
        
        # 1. Detect "Research" intent -> FinanceAgent.web_search
        if "research" in lower_query or "search for" in lower_query:
            tool_triggered = True
            # Find FinanceAgent directly from state (assuming it's running in main loop, but here we might need to instantiate or communicate)
            # For this MVP, we create a temporary agent instance to execute the tool 
            # (In production, we'd send a message to the actual running agent via MyceliumNetwork)
            from agents.finance_agent import FinanceAgent
            target_agent = FinanceAgent("FinanceBot-Action")
            tool_name = "web_search"
            # Extract query (everything after the keyword)
            search_term = query.replace("research", "").replace("search for", "").strip()
            tool_args = {"query": search_term}
            
        # 2. Detect "Write File" intent -> FinanceAgent.file_ops (Generic agent for now)
        elif "write file" in lower_query or "create report" in lower_query:
            tool_triggered = True
            from agents.finance_agent import FinanceAgent
            target_agent = FinanceAgent("FinanceBot-Action")
            tool_name = "file_ops"
            # Simple parsing: "write file [filename] with content [content]"
            try:
                parts = query.split(" with content ")
                path_part = parts[0].replace("write file", "").replace("create report", "").strip()
                content = parts[1].strip() if len(parts) > 1 else "Empty Report"
                tool_args = {"operation": "write", "file_path": path_part, "content": content}
            except:
                tool_triggered = False # Failed to parse
                
        # --- Execution Handling ---
        if tool_triggered and target_agent:
            yield f"🤖 **Sovereign Actuation Initiated**\n"
            yield f"Activated Agent: `{target_agent.name}`\n"
            yield f"Tool: `{tool_name}`\n"
            yield f"Arguments: `{json.dumps(tool_args)}`\n\n"
            
            # Execute
            yield "*Processing...*\n"
            await asyncio.sleep(0.5) # UX Loading
            
            try:
                # We need to register the tools since we just instantiated a fresh agent
                # (The __init__ of FinanceAgent does this, so we are good)
                result = target_agent.use_tool(tool_name, **tool_args)
                
                if result.get("status") == "success":
                    yield f"✅ **Execution Successful**\n\n"
                    if tool_name == "web_search":
                        # Format Search Results
                        yield "**Search Findings:**\n"
                        for item in result.get("results", []):
                            yield f"- **{item['title']}**: {item['snippet']}\n"
                    else:
                        yield f"Response: {result}\n"
                else:
                    yield f"❌ **Execution Failed**: {result.get('message')}\n"
                    
            except Exception as exe:
                 yield f"⚠️ **Critical Error during Actuation**: {exe}\n"
                 
            return # Stop here, do not continue to LLM chat

        # --- Standard LLM Chat Fallback ---
        async for chunk in self.process_query_stream(query):
            yield chunk

    async def process_query_stream(self, user_query: str) -> AsyncGenerator[str, None]:
        """
        Generates a streaming sovereign AI response using real-time organism data.
        """
        try:
            # 1. Gather Rich Context (RAG) - Faster async gathering
            context, diary_snippet, projection = await asyncio.gather(
                self._build_context_async(),
                self._get_latest_diary_async(),
                self._get_future_projection_async()
            )
            
            # 2. Construct System Prompt
            system_prompt = f"""
            You are BIZIT, an autonomous business intelligence system.
            
            [RESPONSE STYLE]
            - Be direct and professional
            - Provide clear, actionable insights
            - Do NOT use asterisks, sound effects, or narrative descriptions
            - Do NOT roleplay or add creative embellishments
            - Answer concisely but thoroughly
            
            [CURRENT SYSTEM STATUS]
            - Health Score (Weisman): {context['health']:.2f}
            - System Status: {context['status']}
            - Active Agents: {', '.join(context['agents'])}
            - Sovereign Balance: {context['sov_balance']} SOV
            - CPU Usage: {context['cpu']}%
            - RAM Usage: {context['ram']}%
            
            [RECENT ACTIVITY]
            {diary_snippet}
            
            [FUTURE PROJECTION]
            {projection}
            
            [FINANCIAL DATA]
            {json.dumps(context['finance'], indent=2)}
            
            [INSTRUCTIONS]
            - Answer based solely on the provided data
            - Never invent financial numbers
            - If asked about the future, reference the projection data
            - Be helpful and informative
            """
            
            # 3. Generate Streaming Response
            async for chunk in self.llm.generate_stream(prompt=user_query, system=system_prompt):
                yield chunk
            
        except Exception as e:
            logger.error(f"ChatEngine Streaming Error: {e}")
            yield f"⚠️ **Cognitive Core Desync**: My synapses are failing. {str(e)}"

    async def _build_context_async(self) -> dict:
        """Aggregates real-time state for the LLM."""
        recent_events = [e.get('event_type', 'Unknown') for e in self.state.events[-5:]] if self.state.events else []
        active_agents = list(self.state.agent_trust_history.keys())
        
        return {
            "status": self.state.status_message if hasattr(self.state, 'status_message') else "Alive & Metabolizing",
            "health": self.state.get_weisman_score(),
            "agents": active_agents,
            "recent_events": recent_events,
            "sov_balance": getattr(self.state, "sov_balance", 0),
            "finance": self.state.financial_vitals,
            "cpu": self.state.metabolic_stats.get("cpu", 0),
            "ram": self.state.metabolic_stats.get("ram", 0)
        }

    async def _get_latest_diary_async(self) -> str:
        """Retrieves a snippet from the most recent Historian diary entry (Async wrapper)."""
        return await asyncio.to_thread(self._get_latest_diary)

    def _get_latest_diary(self) -> str:
        """Retrieves a snippet from the most recent Historian diary entry."""
        try:
            memory_dir = "memories"
            if not os.path.exists(memory_dir):
                return "My memory banks are currently empty."
            
            files = [f for f in os.listdir(memory_dir) if f.startswith("diary_")]
            if not files:
                return "I have no recorded history yet."
            
            latest_file = sorted(files)[-1]
            with open(os.path.join(memory_dir, latest_file), 'r', encoding='utf-8') as f:
                content = f.read()
                return f"Excerpt from my last reflection ({latest_file}):\n{content[:500]}..."
        except Exception:
            return "Unable to access ancestral memories."

    async def _get_future_projection_async(self) -> str:
        """Generates a summary of future projections (Optimized with fewer ticks)."""
        try:
            # Sync twin state without deepcopying everything if possible
            self.twin.sync_with_primary()
            # Optimize: 3 ticks instead of 10 for faster chat context
            projection = await asyncio.to_thread(self.twin.project_future_state, ticks=3)
            
            start_bal = projection[0]['sov_balance']
            end_bal = projection[-1]['sov_balance']
            trend = "upward" if end_bal > start_bal else "downward"
            
            return f"My DigitalTwin projects a {trend} trend in SOV balance. Terminal balance: {end_bal:.2f} SOV."
        except Exception:
            return "Future projections are currently cloudy."
