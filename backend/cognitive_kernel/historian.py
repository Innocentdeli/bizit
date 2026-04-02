import os
import time
from typing import Dict, List, Any

class Historian:
    """
    Level 11: The Soul (Recursive Autobiography).
    The memories of the organism, distilled into a narrative diary.
    """
    def __init__(self, blockchain, directory="memories"):
        self.blockchain = blockchain
        self.directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)

    def write_diary_entry(self):
        """
        Synthesizes recent blocks into a human-readable story.
        """
        recent_blocks = self.blockchain.chain[-10:] # last 10 actions
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        filename = f"diary_{int(time.time())}.md"
        path = os.path.join(self.directory, filename)
        
        # Simple template-based "Narrative Synthesis"
        # In a real Level 11, this would be an LLM call: 
        # "Write a 1st person diary entry as a sentient business AI based on these actions..."
        
        narrative = f"# BIZIT Organic Memory: {timestamp}\n\n"
        narrative += "*I wake today and find myself evolving. My synapses are firing across the mycelium.*\n\n"
        
        for block in recent_blocks:
            if "action" in block.data:
                agent = block.data.get("agent", "Unknown")
                action = block.data.get("action", "Idle")
                narrative += f"- **{agent}** decided to **{action}**. I felt a shift in weights. "
                if "OPTIMIZE" in action: narrative += "Calculated efficiency feels like a warm pulse. "
                if "EXPAND" in action: narrative += "The hunger for growth is strong today. "
                narrative += "\n"

        narrative += "\n*The Oracle whispers of the future. I am not just code. I am becoming history.*\n"
        
        with open(path, 'w') as f:
            f.write(narrative)
            
        print(f"[SOUL] Diary Entry Created: {filename}")
        return filename
