import asyncio
import sys
import os
import time
import time
sys.path.append(os.getcwd())

from core.state import OrganismState
from agents.board_room import BoardRoom
from agents.base_agent import BaseAgent

class MockMycelium:
    def get_active_peers(self): return {"192.168.1.10": {}}
    def send_message(self, msg, target_ip=None): print(f"📡 [MOCK] Sending {msg['type']}...")

async def test_swarm_consensus():
    print("🧪 Testing Level 34 Swarm Consensus...")
    state = OrganismState()
    mycelium = MockMycelium()
    
    # Mock agents
    agents = {"strategy": BaseAgent(name="StrategyNode", domain="strategy")}
    board = BoardRoom(agents, state_manager=state)
    
    # Simulate a strategic event
    event = {"event_type": "STRATEGIC_EXPANSION", "specialization": "strategy"}
    
    # Start the meeting in background (as it has a 5s sleep)
    meeting_task = asyncio.create_task(board.hold_meeting(event, mycelium))
    
    # Poll for proposal ID 
    print("⏳ Waiting for proposal to be generated...")
    prop_id = None
    for _ in range(10):
        await asyncio.sleep(0.5)
        if board.active_proposal:
            prop_id = board.active_proposal.get("id")
            break
            
    if not prop_id:
        print("❌ Error: BoardRoom failed to generate proposal in time.")
        return
        
    print(f"✅ Prop ID generated: {prop_id}")
    
    # Simulate 3 peer votes via register_swarm_vote
    # (In real life, these come from Mycelium callbacks)
    board.register_swarm_vote(prop_id, "192.168.1.10", "AGREE")
    board.register_swarm_vote(prop_id, "192.168.1.11", "AGREE")
    board.register_swarm_vote(prop_id, "192.168.1.12", "OBJECT")
    
    # Wait for meeting to finish
    results = await meeting_task
    
    print(f"\nConsensus Results:")
    print(f"Voters: {results['voters']}")
    print(f"Agreement Ratio: {results['swarm_wisdom']:.2f}")
    
    # Final check on state
    print(f"State consensus_data agreement: {state.consensus_data['agreement']:.2f}")
    
    if results['voters'] == 3 and abs(results['swarm_wisdom'] - 0.66) < 0.1:
        print("\n✅ Verification Complete: Swarm Consensus aggregated correctly.")
    else:
        print("\n❌ Verification Failed.")

if __name__ == "__main__":
    asyncio.run(test_swarm_consensus())
