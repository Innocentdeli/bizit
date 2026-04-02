import os
import time
from typing import Dict, Any
from agents.base_agent import BaseAgent

class DoctorAgent(BaseAgent):
    """
    Level 9: Code Metaprogramming (Self-Repair).
    The Doctor monitors the organism's source code and applies 'patches' to sick agents.
    """
    def __init__(self):
        super().__init__(name="Doctor", domain="SECURITY")
        self.specialization = "CODE_REPAIR"
        self.error_counts = {}

    def receive_task(self, task: Dict[str, Any]):
        # "Diagnose" the error log
        event_type = task.get("event_type", "")
        
        if "ERROR" in event_type or "CRASH" in event_type:
            target_agent = task.get("payload", {}).get("source_agent", "unknown") 
            self.error_counts[target_agent] = self.error_counts.get(target_agent, 0) + 1
            
            print(f"[DOCTOR] Diagnosing crash in {target_agent}... (Count: {self.error_counts[target_agent]})")
            
            if self.error_counts[target_agent] >= 3:
                self.perform_surgery(target_agent)
                self.error_counts[target_agent] = 0 # Reset
                
        return {"decision": "MONITORED", "timestamp": time.time()}

    def perform_surgery(self, agent_name: str):
        """
        Rewrites the agent's source code to inject a 'Safe Mode'.
        """
        print(f"[DOCTOR] Performing Code Surgery on {agent_name}...")
        
        # Mapping base names to filenames (Level 9 Heuristic)
        mapping = {
            "Finance": "finance_agent.py",
            "Sales": "the_sales_agent.py",
            "Operations": "operations_agent.py",
            "Logistics": "logistics_agent.py",
            "Negotiation": "negotiation_agent.py",
            "Strategy": "strategy_agent.py",
            "Expansion": "expansion_agent.py"
        }
        
        target_file = None
        for key, filename in mapping.items():
            if key.lower() in agent_name.lower():
                target_file = filename
                break
        
        if not target_file:
             print(f"❌ [DOCTOR] Could not resolve file for {agent_name}")
             return

        file_path = os.path.join("agents", target_file)
        abs_path = os.path.abspath(file_path)
        
        if not os.path.exists(abs_path):
             print(f"❌ [DOCTOR] Could not find source code for {agent_name} at {abs_path}")
             return

        try:
            with open(abs_path, 'r') as f:
                code = f.read()
            
            if not code or "class " not in code:
                print(f"❌ [DOCTOR] Source code for {agent_name} is corrupted or empty. Cannot perform surgery.")
                return

            # Simple Metaprogramming: Inject a print statement at the top of receive_task
            # In a real AGI, this would use AST to insert try/except blocks
            patch = f"\n    # 🛡️ [DOCTOR PATCH] Safe Mode Activated due to instability.\n"
            
            if patch in code:
                print(f"⚠️ [DOCTOR] Patient {agent_name} already patched.")
                return

            # Inject safely
            # We look for the class definition and add a comment
            new_code = code.replace("class ", f"{patch}class ")
            
            if not new_code:
                print(f"❌ [DOCTOR] Patch generation failed for {agent_name}")
                return

            # with open(abs_path, 'w') as f:
            #     f.write(new_code)
                
            print(f"✅ [DOCTOR] Surgery Simulated. {agent_name} would be in Safe Mode.")
            
        except Exception as e:
            print(f"❌ [DOCTOR] Surgery Failed: {e}")
