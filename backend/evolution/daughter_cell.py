import asyncio
import threading
import time
import logging
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from cognitive_kernel.local_llm_client import LocalLLMClient

logger = logging.getLogger(__name__)

class DaughterCell(threading.Thread):
    """
    A lightweight, ephemeral agent instance spawned via Mitosis.
    Inherits 'DNA' (Context) and task-specific instructions.
    Terminates automatically after task completion (Apoptosis).
    """
    def __init__(self, cell_id: str, role: str, task: Dict[str, Any], parent_results: List[Dict[str, Any]]):
        super().__init__()
        self.cell_id = cell_id
        self.role = role
        self.task = task
        self.results_ref = parent_results
        self.status = "GESTATION"
        self.is_alive_signal = True
        
        # Initialize minimal intelligence
        self.llm = LocalLLMClient()

    def run(self):
        self.status = "ACTIVE"
        logger.info(f"🐣 [MITOSIS] Daughter Cell {self.cell_id} ({self.role}) initialized and active.")
        
        try:
            # 1. Prepare Reasoning Prompt
            prompt = f"""
            You are a Daughter Cell (Worker Node) of the BIZIT organism.
            Identity: {self.cell_id}
            Specialization: {self.role}
            
            TASK: {self.task.get('description', 'No description')}
            TARGET: {self.task.get('target', 'No target')}
            
            Perform this specific task concisely and return the result.
            """
            
            # 2. Execute Intelligence Cycle (Use asyncio.run for thread safety with async method)
            logger.info(f"🧠 [MITOSIS] {self.cell_id} performing reasoning cycle...")
            response = asyncio.run(self.llm.generate(prompt))
            
            # 3. Report Result to Parent (Colony Memory)
            result_payload = {
                "cell_id": self.cell_id,
                "role": self.role,
                "result": response,
                "timestamp": time.time(),
                "status": "SUCCESS"
            }
            self.results_ref.append(result_payload)
            logger.info(f"✅ [MITOSIS] {self.cell_id} task complete. Result reported.")

        except Exception as e:
            logger.error(f"💀 [MITOSIS] {self.cell_id} failed: {e}")
            self.results_ref.append({
                "cell_id": self.cell_id,
                "error": str(e),
                "status": "FAILED"
            })
        
        finally:
            self.apoptosis()

    def apoptosis(self):
        """Clean termination of the cell."""
        self.status = "APOPTOSIS"
        self.is_alive_signal = False
        logger.info(f"🍂 [MITOSIS] Daughter Cell {self.cell_id} undergoing apoptosis. Resources returned to Mother.")
