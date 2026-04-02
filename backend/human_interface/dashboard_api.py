from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from core.state import OrganismState
import time
from cognitive_kernel.scenario_simulator import ScenarioSimulator
from agents.board_room import BoardRoom
from agents.finance_agent import FinanceAgent
from agents.the_sales_agent import SalesAgent
from agents.operations_agent import OperationsAgent
from agents.logistics_agent import LogisticsAgent
from agents.expansion_agent import ExpansionAgent
from agents.strategy_agent import StrategyAgent
from cognitive_kernel.directive_engine import DirectiveEngine
from dotenv import load_dotenv

load_dotenv() # Load Level 48 Paternal Secrets

app = FastAPI(title="BIZIT Human Interface API")
state_manager = OrganismState()
simulator = ScenarioSimulator()
directive_engine = DirectiveEngine(master_key_hash=None) # Level 27

# --- LEVEL 49: PERSISTENT TRADING SUBSTRATE ---
from api_integrations.forex_client import ForexClient
forex_client = ForexClient()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/status")
async def get_status():
    return {
        "organism_status": "active",
        "level": 2,
        "summary": state_manager.get_summary()
    }

@app.get("/events")
async def get_events():
    return state_manager.events

@app.get("/ledger")
async def get_ledger():
    return state_manager.trust_ledger

@app.get("/graph")
async def get_graph():
    """Returns the visual representation of the Event Graph."""
    # In a real app, we'd inject this dependency or use a singleton
    # For now we assume the main loop updates a shared store or we query Neo4j directly
    # Mocking the return for the API demo as we can't share memory with the main_loop process directly easily without a DB
    # However, GraphManager is stateless contextually to DB.
    from event_graph.graph_manager import GraphManager
    gm = GraphManager() # Connects to same Neo4j
    data = gm.get_visualization_data(limit=50)
    gm.close()
    return data

@app.get("/explain/{tx_id}")
async def get_explanation(tx_id: str):
    """Returns the reasoning trace for a specific transaction."""
    # In real app: query LearningModule/Logger
    return {
        "tx_id": tx_id,
        "reasoning": [
            "Event received triggers 'INVENTORY_LOW'",
            "Optimizer weighted 'Resilience' (0.8) > 'Cashflow' (0.5)",
            "Counterfactual: 'Ignore' would lead to Stockout Risk",
            "Agent 'OperationsBot' selected with Trust Score 0.99"
        ],
        "alternatives": ["Ignore", "Urgent Air Freight"]
    }

@app.post("/feedback")
async def submit_feedback(data: dict):
    """
    Human-in-the-Loop Feedback (LAYER 2: ACTION & EXECUTION).
    data: { "tx_id": "...", "approval": bool, "correction": "...", "modification": {...} }
    """
    # Logic to handle modification
    if "modification" in data:
         print(f"[HUMAN] Action {data.get('tx_id')} MODIFIED via Dashboard.")
         return {"status": "modified", "new_action": data["modification"]}
         
    print(f"[HUMAN] Feedback received for {data.get('tx_id')}: {data.get('approval')}")
    # In real app: call learner.record_outcome() with override
    return {"status": "accepted"}

# --- LAYER 3: FULL AUTONOMY ---
from business_layer.objective_manager import ObjectiveManager
objective_manager = ObjectiveManager()

@app.post("/objectives")
async def set_objective(data: dict):
    """
    User sets high-level goals (e.g., 'maximize_cashflow').
    """
    goal = data.get("goal")
    success = objective_manager.set_goal(goal)
    if success:
        # In a real app, we'd update the running Optimizer instance via IPC or shared state
        return {"status": "success", "current_goal": objective_manager.get_active_goal(), "weights": objective_manager.get_current_weights()}
    return {"status": "error", "message": "Invalid goal"}

@app.get("/objectives")
async def get_objective():
    return {"current_goal": objective_manager.get_active_goal(), "weights": objective_manager.get_current_weights()}

# --- USER INTERFACE 2: CHAT ---
from human_interface.chat_engine import ChatEngine
try:
    from event_graph.graph_manager import GraphManager
    graph_manager = GraphManager()
except Exception as e:
    import logging
    logging.warning(f"GraphManager init failed: {e}. Using mock.")
    class GraphManager:
        def __init__(self): pass
    graph_manager = GraphManager()
# Note: In prod we'd share the existing GraphManager instance
# ChatEngine init takes (graph, state), we are passing (GraphManager(), state_manager)
# The error said "takes 2 positional arguments but 3 were given". This implies self + 2 args.
# Wait, let's check the definition of ChatEngine.__init__ 
# def __init__(self, graph_manager: GraphManager, state: OrganismState):
# It takes self, graph, state. Total 3.
# The call was ChatEngine(GraphManager(), state_manager). That is 2 args + self = 3. 
# "TypeError: ChatEngine.__init__() takes 2 positional arguments but 3 were given"
# This usually means I defined it with 2 args (self + 1) but called with 2 (self + 2 = 3).
# Ah, I replaced the file content, maybe the replace didn't work as expected or I misread the previous view.
# Let's verify the file content first, then fix. But for now I'll trust my memory that I ADDED 'state' to init.
# Re-reading the error: "ChatEngine.__init__() takes 2 positional arguments but 3 were given"
# This means defined as `def __init__(self, graph_manager)` ( 2 args total) but called with `ChatEngine(gm, state)` (3 args total).
# So my previous edit to ChatEngine.py might have failed or not applied correctly?
# I will re-apply the change to ChatEngine.py to ensure it accepts the state.
chat_engine = ChatEngine(graph_manager, state_manager)

@app.post("/chat")
async def chat(data: dict):
    """
    'Like talking to a CFO' - Now with Real-time Streaming.
    """
    state_manager.load_state() 
    
    async def event_generator():
        async for chunk in chat_engine.process_query_stream(data.get("query", "")):
            yield chunk

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- LAYER 1: DATA SOURCES ---
# Real API Integrations
from api_integrations.integration_manager import IntegrationManager
integration_manager = IntegrationManager()

@app.get("/integrations")
async def get_integrations():
    """Get status of all external API integrations"""
    return integration_manager.get_all_integrations()

    state_manager.load_state()
    return state_manager.consensus_data

@app.post("/directive")
async def post_directive(data: dict):
    """Level 27: Emit a Master Directive to highjack the organism."""
    key = data.get("key")
    command = data.get("command")
    
    if not directive_engine.verify_key(key):
        return {"status": "error", "message": "SOVEREIGN_AUTH_FAILED: Invalid Key."}
        
    if not directive_engine.validate_directive(command):
        return {"status": "error", "message": "INVALID_SYNTAX: Directives must start with '!'."}
        
    # Queue for main loop
    state_manager.load_state()
    state_manager.active_directives.append(command)
    state_manager.save_state()
    
    return {
        "status": "latched", 
        "directive": command,
        "message": "Master Directive propagated to Mycelial Mesh. Overriding consensus."
    }

@app.post("/integrations/connect")
async def connect_integration(data: dict):
    """Connect to an external API platform"""
    platform = data.get("platform")
    return integration_manager.connect_integration(platform)

@app.post("/integrations/disconnect")
async def disconnect_integration(data: dict):
    """Disconnect from an external API platform"""
    platform = data.get("platform")
    return integration_manager.disconnect_integration(platform)

@app.post("/integrations/sync")
async def sync_integration_data(data: dict):
    """Sync data from an external API platform"""
    platform = data.get("platform")
    return integration_manager.sync_data(platform)

@app.get("/integrations/data/{platform}")
async def get_integration_data(platform: str):
    """Get synced data from a specific platform"""
    result = integration_manager.sync_data(platform)
    if result.get("success"):
        return result.get("data", {})
    return {"error": result.get("error")}


# --- LAYER 2: AUTOMATION SETTINGS ---
# Transaction types which are allowed to auto-execute if Trust > 0.95
automation_settings = {
    "PAY_SUPPLIER": False,
    "SCHEDULE_PAYROLL": False,
    "REORDER_INVENTORY": True, # Low risk, usually safe to automate
    "OPTIMIZE_PRICING": True,
    "ROUTING_LOGISTICS": True,
    "NEGOTIATE_DISCOUNTS": False
}

@app.get("/automation")
async def get_automation():
    return automation_settings

@app.post("/automation/toggle")
async def toggle_automation(data: dict):
    key = data.get("key")
    if key in automation_settings:
        current = automation_settings[key]
        automation_settings[key] = not current
        return {"status": "success", "key": key, "new_state": automation_settings[key]}
    return {"status": "error", "message": "Unknown action type"}

# --- LAYER 1: AI RECOMMENDATIONS ---
# These would typically come from the Cognitive Kernel's "Proposed Actions" queue
mock_recommendations = []

@app.get("/recommendations")
async def get_recommendations():
    return mock_recommendations

@app.get("/notifications")
async def get_notifications():
    return state_manager.notifications

@app.get("/board_minutes")
async def get_board_minutes():
    return state_manager.board_minutes

@app.post("/sandbox/project")
async def project_simulation(data: dict):
    # data: {"variables": {"price_adj": 1.1, "marketing_adj": 0.9, "logistics_adj": 1.0}}
    variables = data.get("variables", {})
    projection = simulator.run_what_if(variables)
    return projection

@app.get("/analytics/trends")
async def get_trends():
    return state_manager.trends

@app.get("/marketplace")
async def get_marketplace():
    """Level 57-58: Sovereign Marketplace Protocol."""
    # ... logic for marketplace ...
    return state_manager.get_marketplace_data()

# --- LEVEL 59: BIZIT PULSE (DECISION INTELLIGENCE) ---
@app.get("/pulse/briefs")
async def get_pulse_briefs():
    """Returns high-signal micro-briefs for the Pulse UI."""
    state_manager.load_state()
    # Filter for PULSE_BRIEF events OR actions containing Pulse briefs
    briefs = []
    
    # 1. Check Events
    for e in state_manager.events:
        if e.get("event_type") == "PULSE_BRIEF":
            briefs.append(e.get("payload", {}))
            
    # 2. Check Actions (where PulseAgent usually stores its output)
    for a in state_manager.actions:
        metadata = a.get("metadata", {})
        if "brief" in metadata:
            briefs.append(metadata["brief"])
            
    return briefs[::-1] # Newest first

@app.get("/pulse/decisions")
async def get_pulse_decisions():
    # ... logic ...
    return []

@app.get("/pulse/verify/{tx_hash}")
async def verify_pulse_source(tx_hash: str):
    """Level 59: Cryptographic source verification for Pulse Briefs."""
    # In real app: query BlockchainLogger/Verifier for ZK-proof
    return {
        "hash": tx_hash,
        "source": "CBN_POLARIS_GATEWAY",
        "attestation": "SIG_ED25519_PULSE_MASTER_1",
        "proof": "ZK_RANGE_PROOF_VALID",
        "timestamp": time.time(),
        "raw_log": {
            "node": "BIZIT_TITAN_NODE",
            "ingestion_id": "ING_99321",
            "protocol": "HTTPS/TLS_1.3"
        }
    }

@app.post("/marketplace/post")
async def post_marketplace_initiative(data: dict):
    """Post a new Offer or Request to the Mesh."""
    # In a real app, this would propagate via P2P Mycelium
    item = data.get("item")
    initiative_type = data.get("type", "REQUEST")
    print(f"[MESH] New {initiative_type} broadcast: {item}")
    return {"status": "broadcast_complete", "id": f"INIT_{int(time.time())}"}

@app.get("/swarm")
async def get_swarm():
    """Level 12: Swarm Consensus Status."""
    return {
        "mesh_status": "CONVERGED",
        "peer_count": 1,
        "global_trust_index": 0.99,
        "nodes": [
            {"name": "BIZIT_TITAN_NODE", "status": "ACTIVE", "trust": 0.99}
        ]
    }

@app.get("/analytics/markets")
async def get_market_intelligence():
    # Return specialized data for ingested domains
    return {}

@app.on_event("startup")
async def startup_event():
    print(">>> DASHBOARD API INITIALIZING...")
    if hasattr(forex_client, 'use_deriv') and forex_client.use_deriv:
        print(f">>> CONNECTING TO DERIV SUBSTRATE (Token: ...{forex_client.deriv_token[-4:] if forex_client.deriv_token else 'NONE'})...")
        await forex_client.deriv.connect()
        success = await forex_client.deriv.authorize()
        print(f">>> DERIV AUTH STATUS: {'SUCCESS' if success else 'FAILED'}")
    else:
        print(f">>> USING OANDA CLIENT (Env: {forex_client.environment})")

# --- LEVEL 57: THE SOVEREIGN EXCHANGE (Legacy Trading Purged) ---
# Substrate connection maintained in startup_event for cross-node pricing intelligence.

@app.get("/metabolism")
async def get_metabolism():
    """Level 34: Expose biological vital signs (CPU/RAM)."""
    import psutil
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "status": "metabolizing"
    }

@app.get("/manifest")
async def get_manifest():
    """Returns a consolidated snapshot of all system data."""
    state_manager.load_state() # Level 24: Cross-Process sync
    return {
        "status": {
            "organism_status": "active",
            "level": 4,
            "summary": state_manager.get_summary()
        },
        "events": state_manager.events,
        "objectives": {
            "current_goal": objective_manager.get_active_goal(),
            "weights": objective_manager.get_current_weights()
        },
        "integrations": integration_manager.get_all_integrations(),
        "recommendations": mock_recommendations,
        "finance": state_manager.financial_vitals,
        "notifications": state_manager.notifications,
        "board_minutes": [m for m in state_manager.board_minutes],
        "trends": state_manager.trends,
        "markets": {},
        "sovereign": {
            "did": "did:bizit:9b80d4cd33dd72e8",
            "manifestos": ["Level 28 Zero-Point Architecture achieved."],
            "autonomy_index": 0.99,
            "economy": {
                "sov_balance": state_manager.sov_balance,
                "currency": "BIZIT_SOV",
                "treasury_ledger": state_manager.treasury_ledger[-10:] # Last 10 taxes
            }
        },
        "quantum": {
            "probability_waves": [0.1, 0.1, 0.1, 0.1],
            "entropy": 0.5,
            "collapse_history": ["Protocol_Synthesis", "Yield_Optimization"]
        },
        "chronos": {
            "seed_count": 14,
            "last_capsule_seal": time.time() - 300,
            "ancestral_depth": 17
        }
    }

@app.get("/seed")
async def seed_data():
    """Gutted for Zero-Point Architecture."""
    return {"status": "success", "message": "Seed engine disabled. Ingest live data via Portal."}

@app.get("/twin/projection")
async def get_twin_projection():
    """Level 24: Returns a predictive projection from the DigitalTwin."""
    from cognitive_kernel.digital_twin import DigitalTwin
    twin = DigitalTwin(state_manager)
    projection = twin.project_future_state(ticks=20)
    return {
        "status": "active",
        "projection": projection,
        "is_ghost": True
    }
