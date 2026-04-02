import random
import time
from event_graph.graph_manager import GraphManager

class DreamEngine:
    """
    Level 8: The Dream State (REM Sleep).
    Consolidates memories when the system is idle.
    """
    def __init__(self, graph_manager: GraphManager):
        self.graph = graph_manager
        self.memories = [] # Short term episodic memory

    def add_memory(self, event):
        """adds a waking experience to the hipocampus (buffer)."""
        self.memories.append(event)
        if len(self.memories) > 100:
            self.memories.pop(0)

    def enter_rem_sleep(self):
        """
        Replays memories to reinforce graph connections.
        Only runs when Metabolic Stress is LOW.
        """
        if not self.memories:
            return "No memories to process."
            
        print("🌙 [SLEEP] Entering REM State... Dreaming...")
        
        # Re-consolidate 3 random memories
        dreams = random.sample(self.memories, min(3, len(self.memories)))
        
        for dream in dreams:
            # Reinforce the graph connection (Hebbian Learning: Neurons that fire together...)
            # We mock this by "updating" the graph again, perhaps with higher weight
            self.graph.update_graph(dream)
            print(f"💤 [DREAM] Replaying event: {dream.get('event_type')}")
            time.sleep(0.5) # Time dilation in dreams
            
        return "Dream Cycle Complete. Synapses reinforced."
