import logging
import time
import uuid
from typing import Dict, Any, List
from .mitosis_engine import MitosisEngine

logger = logging.getLogger(__name__)

class ConsensusEngine:
    """
    Implements the "Swarm Consensus" protocol.
    Spawns multiple Daughter Cells to review and vote on high-stakes actions.
    Level 38: Collective Intelligence.
    """
    def __init__(self, mitosis_engine: MitosisEngine):
        self.mitosis = mitosis_engine
        self.active_debates: Dict[str, Dict[str, Any]] = {}

    def propose_consensus_action(self, action_type: str, details: Dict[str, Any], swarm_size: int = 3) -> str:
        """
        Initiates a new debate. Spawns `swarm_size` jury cells.
        """
        debate_id = f"DEBATE-{str(uuid.uuid4())[:8].upper()}"
        logger.info(f"🏛️ [CONSENSUS] New Debate Initialized: {debate_id} ({action_type})")
        
        self.active_debates[debate_id] = {
            "type": action_type,
            "details": details,
            "votes": [],
            "status": "VOTING",
            "start_time": time.time(),
            "required_votes": swarm_size
        }
        
        # Spawn the jury
        for i in range(swarm_size):
            task_context = {
                "description": f"REVIEW CRITICAL ACTION: {action_type}. Details: {details}",
                "target": f"DEBATE_{debate_id}_VOTER_{i}",
                "is_consensus_vote": True
            }
            role = "JuryNode"
            self.mitosis.spawn_cell(role, task_context)
            
        return debate_id

    def update_consensus_state(self):
        """
        Checks MitosisEngine results and applies them to active debates.
        """
        # Get results from the colony
        stats = self.mitosis.monitor_colony()
        results = stats.get("recent_results", [])
        
        for res in results:
            # Check if this result belongs to an active debate
            # Using a simple substring check for the target 'DEBATE_{id}'
            for debate_id, debate in self.active_debates.items():
                if f"DEBATE_{debate_id}" in res.get("cell_id", "") or debate_id in str(res): # Looser match for simulation
                    # Check for keywords in the LLM response to determine vote
                    content = res.get("result", "").upper()
                    vote = "APPROVE" if any(kw in content for kw in ["DONE", "SUCCESS", "YES", "APPROVE", "POSITIVE"]) else "REJECT"
                    
                    # Prevent double counting
                    already_voted = any(v["cell_id"] == res["cell_id"] for v in debate["votes"])
                    if not already_voted:
                        debate["votes"].append({
                            "cell_id": res["cell_id"],
                            "vote": vote,
                            "reasoning": res.get("result", "")[:200]
                        })
                        logger.info(f"🗳️ [CONSENSUS] Debate {debate_id}: Vote received from {res['cell_id']} ({vote})")

    def get_debate_result(self, debate_id: str) -> Dict[str, Any]:
        """
        Determines the outcome of a debate.
        """
        debate = self.active_debates.get(debate_id)
        if not debate:
            return {"status": "NOT_FOUND"}
            
        votes = debate["votes"]
        if len(votes) < debate["required_votes"]:
            return {
                "status": "VOTING_IN_PROGRESS",
                "current_vote_count": len(votes),
                "required": debate["required_votes"]
            }
            
        approvals = sum(1 for v in votes if v["vote"] == "APPROVE")
        threshold = (debate["required_votes"] // 2) + 1 # Simple majority
        
        passed = approvals >= threshold
        debate["status"] = "PASSED" if passed else "FAILED"
        
        return {
            "status": "COMPLETED",
            "outcome": "PASSED" if passed else "FAILED",
            "approvals": approvals,
            "total_votes": len(votes),
            "votes": votes
        }
