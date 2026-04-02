import threading
import uuid
import logging
from typing import Dict, Any, List
from .daughter_cell import DaughterCell

logger = logging.getLogger(__name__)

class MitosisEngine:
    """
    Manages the lifecycle of Daughter Cells (Spawning, Monitoring, Culling).
    """
    def __init__(self):
        self.colony: Dict[str, DaughterCell] = {}
        self.results_queue: List[Dict[str, Any]] = []

    def spawn_cell(self, role: str, task_context: Dict[str, Any]) -> str:
        """
        Triggers Mitosis: Spawns a new Daughter Cell.
        """
        cell_id = f"CELL-{str(uuid.uuid4())[:8].upper()}"
        
        # Create the organism
        new_cell = DaughterCell(cell_id, role, task_context, self.results_queue)
        
        # Register in colony
        self.colony[cell_id] = new_cell
        
        # Ignite spark of life (Start Thread)
        new_cell.start()
        
        return cell_id

    def monitor_colony(self) -> Dict[str, Any]:
        """
        Returns the vital signs of the colony.
        """
        # Cleanup dead cells
        active_cells = {cid: cell for cid, cell in self.colony.items() if cell.is_alive()}
        dead_cells = set(self.colony.keys()) - set(active_cells.keys())
        
        # Remove dead cells references (Garbage Collection)
        for cid in dead_cells:
            del self.colony[cid]

        return {
            "colony_size": len(active_cells),
            "active_cells": [
                {"id": c.cell_id, "role": c.role, "status": c.status} 
                for c in active_cells.values()
            ],
            "recent_results": self.results_queue[-5:] # Show last 5
        }
    
    def trigger_mass_apoptosis(self):
        """Kill switch for the colony."""
        for cell in self.colony.values():
            cell.apoptosis() # Signal death (though thread join is needed for hard stop)
        self.colony.clear()
