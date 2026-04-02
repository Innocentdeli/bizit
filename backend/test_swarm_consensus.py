import sys
sys.path.append(".")
import time
import logging
import asyncio
from evolution.mitosis_engine import MitosisEngine
from evolution.consensus_engine import ConsensusEngine
from agents.finance_agent import FinanceAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def test_swarm_consensus():
    print("🏛️ Testing Level 38: Swarm Consensus (Collective Intelligence)...")
    print("=" * 60)
    
    mitosis = MitosisEngine()
    consensus = ConsensusEngine(mitosis)
    finance = FinanceAgent()
    
    # Simulate a high-stakes DeFi event
    print("\n[STEP 1] Simulating High-Stakes DeFi Event ($500 Trade)")
    # We trigger a buy signal on an even price
    simulated_state = {
        "event_type": "DEFI_TICK",
        "payload": {
            "instrument": "BTC_USDC",
            "price": 95000.02 # Even price triggers buy
        }
    }
    
    # Inject mock vitals to allow the trade
    finance.state_vitals = {"defi": {"usdc_balance": 5000.0, "gas_eth": 0.1}}
    
    # 1. Agent Reasoning
    decision = finance.reason(simulated_state)
    print(f"🧐 Agent Decision: {decision['decision']}")
    
    if decision['decision'] == "PROPOSE_CONSENSUS":
        print(f"✅ Detection Success: Action flagged as High-Stakes. Reason: {decision['metadata'].get('reason')}")
        
        # 2. Initiate Consensus
        debate_id = consensus.propose_consensus_action(
            decision['metadata']['action'], 
            decision['metadata'],
            swarm_size=3
        )
        print(f"🏛️ Debate {debate_id} initiated. Spawning 3 Jury Nodes...")
        
        # 3. Monitor for votes
        print("\n[STEP 2] Monitoring Swarm Debate...")
        for i in range(20): # Give it up to 20 seconds for the swarm to think
            consensus.update_consensus_state()
            result = consensus.get_debate_result(debate_id)
            
            print(f"   T+{i}s | Status: {result['status']} | Votes: {result.get('current_vote_count', result.get('total_votes', 0))}/3")
            
            if result['status'] == "COMPLETED":
                break
            await asyncio.sleep(1)
            
        # 4. Final Verdict
        if result['status'] == "COMPLETED":
            print(f"\n[STEP 3] Collective Verdict Reached")
            print(f"✅ Outcome: {result['outcome']}")
            print(f"📊 Approvals: {result['approvals']}/{result['total_votes']}")
            for v in result['votes']:
                print(f"   - {v['cell_id']}: {v['vote']} (Reason: {v['reasoning'][:50]}...)")
        else:
            print("\n❌ Verification Failed: Swarm did not reach consensus in time.")
            
    else:
        print(f"❌ Verification Failed: Agent decided to {decision['decision']} directly.")

if __name__ == "__main__":
    asyncio.run(test_swarm_consensus())
