from typing import List, Dict, Any, Any
import asyncio
import time
from agents.base_agent import BaseAgent

class BoardRoom:
    """
    Manages collaborative decision making (Phase 1: Agent Board Room).
    Triggered for 'STRATEGIC' events requiring cross-domain consensus.
    """
    def __init__(self, agents: Dict[str, BaseAgent], state_manager: Any = None):
        self.agents = agents
        self.state_manager = state_manager
        self.meeting_history = []
        self.active_proposal = None # Level 34
        self.active_votes = {} # {proposal_id: {peer_ip: status}}
        self.consensus_summary = {"agreement": 0.0, "voters": 0, "active_proposal": None}

    async def hold_meeting(self, event: Dict[str, Any], mycelium=None) -> Dict[str, Any]:
        """
        Orchestrates a debate between agents and aggregates global swarm consensus.
        """
        event_type = event.get("event_type", "UNKNOWN")
        proposal_id = f"PROP_{int(time.time())}"
        print(f"\n[BOARD ROOM] Meeting Convened: {event_type} (Proposal: {proposal_id})")
        
        minutes = {
            "proposal_id": proposal_id,
            "event": event_type,
            "debate": [],
            "consensus": None,
            "final_decision": None,
            "swarm_wisdom": 0.0,
            "voters": 0
        }

        # 1. Auction Phase (Internal Consensus)
        primary_agent_type = event.get("specialization", "strategy")
        participants = [self.agents.get(primary_agent_type, self.agents["strategy"])]
        peers = [a for k, a in self.agents.items() if k != primary_agent_type and k != "strategy"]
        participants.extend(peers[:2])
        
        winning_bid = 0.0
        winner = None
        for agent in set(participants):
            bid = agent.bid_for_action(event)
            if bid > winning_bid:
                winning_bid = bid
                winner = agent
        
        if not winner: winner = self.agents["strategy"]
        primary_proposal = winner.propose_action(event)
        
        self.active_proposal = {**primary_proposal, "id": proposal_id}
        self.active_votes[proposal_id] = {}
        
        # Sync Initial Proposal to State
        if self.state_manager:
            self.state_manager.update_consensus_stats({
                "active_proposal": primary_proposal.get("decision"),
                "agreement": 0.0,
                "voters": 0
            })

        # 2. THE GLOBAL SWARM (Swarm Intelligence)
        if mycelium:
            active_peers = mycelium.get_active_peers()
            if active_peers:
                print(f"[BOARD ROOM] 📡 Broadcasting Proposal {proposal_id} to {len(active_peers)} nodes...")
                mycelium.send_message({
                    "type": "CONSENSUS_PROPOSAL",
                    "proposal_id": proposal_id,
                    "decision": primary_proposal['decision'],
                    "event_type": event_type
                })
                
                # Level 34: 5-Second Voting Window
                print(f"[BOARD ROOM] ⏳ Opening 5s Voting Window for Swarm Consensus...")
                await asyncio.sleep(5.0) 
                
                votes = self.active_votes.get(proposal_id, {})
                voters = len(votes)
                if voters > 0:
                    agreements = sum(1 for v in votes.values() if v == "AGREE")
                    agreement_ratio = agreements / voters
                    minutes["swarm_wisdom"] = agreement_ratio
                    minutes["voters"] = voters
                    self.consensus_summary = {"agreement": agreement_ratio, "voters": voters, "active_proposal": None}
                    
                    if self.state_manager:
                        self.state_manager.update_consensus_stats(self.consensus_summary)
                        
                    print(f"[BOARD ROOM] ✅ Swarm Consensus Aggregated: {agreement_ratio*100:.1f}% Agreement ({voters} votes)")
                else:
                    print(f"[BOARD ROOM] ⚠️ No swarm votes received. Proceeding with local heuristics.")

        # 3. Finalization
        minutes["consensus"] = "Swarm Validated" if minutes["voters"] > 0 else "Internal Majority"
        minutes["final_decision"] = primary_proposal
        
        self.meeting_history.append(minutes)
        self.active_proposal = None # Reset
        
        # Clear Consensus Stats after meeting
        if self.state_manager:
            self.state_manager.update_consensus_stats({"active_proposal": None, "agreement": 0.0, "voters": 0})
            
        return minutes

    def register_swarm_vote(self, proposal_id: str, peer_ip: str, vote: str):
        """Callback for Mycelium to pulse in swarm votes."""
        if proposal_id in self.active_votes:
            self.active_votes[proposal_id][peer_ip] = vote
            print(f"🐝 [SWARM] Registered {vote} from {peer_ip} for {proposal_id}")
            
            # Real-time sync of partial consensus results
            if self.state_manager:
                votes = self.active_votes[proposal_id]
                voters = len(votes)
                agreements = sum(1 for v in votes.values() if v == "AGREE")
                ratio = agreements / voters
                self.state_manager.update_consensus_stats({"agreement": ratio, "voters": voters})

    def simulate_peer_comment(self, agent: BaseAgent, proposal: Dict[str, Any]):
        """Mocked debate logic."""
        import random
        scores = ["AGREE", "CONCERN", "OBJECT"]
        weights = [0.7, 0.2, 0.1]
        status = random.choices(scores, weights=weights)[0]
        
        comments = {
            "AGREE": "Aligns with my domain metrics.",
            "CONCERN": "Slight risk to my resource budget.",
            "OBJECT": "Conflict detected with ongoing initiatives."
        }
        
        return {"status": status, "comment": comments[status]}

    def get_latest_minutes(self):
        return self.meeting_history[-1] if self.meeting_history else None
