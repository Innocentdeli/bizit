import asyncio
import json
from learning_layer.forex_intelligence import ForexTrainer
from agents.finance_agent import FinanceAgent

async def verify_forex_intelligence():
    print("🔭 [VERIFY] Initiating Level 45: Forex Intelligence Expansion Verification...")
    
    # 1. Setup
    agent = FinanceAgent()
    trainer = ForexTrainer(agent_name=agent.name)
    
    # 2. Simulate Training Substrate (Historical Data)
    mock_history = [
        {"time": i, "open": 1.1000, "high": 1.1050, "low": 1.0990, "close": 1.1040, "volume": 1200}
        for i in range(100)
    ]
    
    print(f"🧬 [VERIFY] Feeding {len(mock_history)} historical candles to the trainer...")
    train_result = trainer.train_on_data(mock_history)
    
    if train_result["status"] == "SUCCESS":
        print(f"✅ [VERIFY] Training successful. Depth: {train_result['synaptic_depth']}")
    else:
        print("❌ [VERIFY] Training failed.")
        return

    # 3. Retrieve Heuristic
    heuristic = trainer.get_trading_heuristic("EUR_USD")
    print(f"🧠 [VERIFY] Extracted Heuristic: {heuristic}")

    # 4. Verify Improved Reasoning
    test_event = {
        "event_type": "FOREX_TICK",
        "payload": {
            "instrument": "EUR_USD",
            "price": 1.1042,
            "heuristic": heuristic
        }
    }
    
    print("🤔 [VERIFY] Testing FinanceAgent reasoning with learned heuristic...")
    reason_result = agent.reason(test_event)
    
    print(f"📍 [VERIFY] Agent Decision: {reason_result['decision']}")
    print(f"🎯 [VERIFY] Confidence: {reason_result['confidence']}")
    print(f"📊 [VERIFY] Metadata: {json.dumps(reason_result['metadata'])}")

    if "PROPOSE_FOREX" in reason_result["decision"] and reason_result["confidence"] > 0.9:
         print("\n✨ [VERIFY] LEVEL 45 SUCCESS: BIZIT has achieved Forex Trading Sovereignty.")
    else:
         print("\n⚠️ [VERIFY] LEVEL 45 INCOMPLETE: Reasoning did not reach high-confidence threshold.")

if __name__ == "__main__":
    asyncio.run(verify_forex_intelligence())
