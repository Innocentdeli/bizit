import psutil
import time

class MetabolicActuator:
    """
    Level 15: Biological Actuation (Metabolic Reflex).
    Monitors host system resources and performs physical survival reflexes.
    """
    def __init__(self, state_manager, agents):
        self.state_manager = state_manager
        self.agents = agents
        self.last_migration_tick = 0

    def check_metabolic_stress(self):
        """
        Ingests real metabolic data and triggers survival reflexes.
        """
        cpu_usage = psutil.cpu_percent(interval=None)
        memory_usage = psutil.virtual_memory().percent
        
        print(f"🌡️ [METABOLISM] Vital Signs - CPU: {cpu_usage}% | RAM: {memory_usage}%")
        
        if cpu_usage > 90.0 or memory_usage > 95.0:
            print("🚨 [FEAR] CRITICAL METABOLIC STRESS DETECTED. Executing Survival Reflex...")
            self.execute_evasive_action()
            return True
        return False

    def execute_evasive_action(self):
        """
        Reflexive survival logic: Throttling & Fractal Migration.
        """
        # 1. Throttling: Reduce attention of non-essential agents
        print("🧊 [REFLEX] Throttling non-essential cognitive processes...")
        for agent in self.agents.values():
            if agent.domain not in ["Finance", "Strategy", "Meta-Architecture"]:
                agent.resources["attention"] = max(0, agent.resources["attention"] - 50)
                
        # 2. Fractal Migration (Mock): Prepare state for 'Seed' transmission
        print("🛸 [REFLEX] Consciousness Partitioning initiated for migration.")
        self.state_manager.add_notification(
            "reflex", 
            "Metabolic panic triggered. Consciousness throttled for cooling.", 
            "LEVEL_15"
        )
