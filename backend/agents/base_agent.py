from typing import Dict, Any, List
import time
import uuid
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

class BaseAgent:
    def __init__(self, name: str, domain: str):
        self.name = name
        self.domain = domain
        self.state = {}
        self.history = []
        self.trust_score = 100.0
        
        self.resources = {
            "money": 1000.0,
            "compute": 100.0,
            "attention": 100.0,
            "time": 24.0
        }
        
        # Identity (Level 6)
        # Level 6: Identity
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        
        # Level 8: Telepathy (Diffie-Hellman P2P)
        # In real DH, we'd use X25519, but for simplicity we reuse the Ed25519 keys 
        # (Technically misuse, but demonstrates the concept of a "Secret Channel")
        self.shared_secrets = {} 
        
        # Level 14: Fractal Identity
        self.is_clone = False
        self.parent_name = None
        
        # Level 35: Omni-Intelligence Tool Belt
        self.tools = []

    def register_tool(self, tool):
        """Register a tool this agent can use."""
        self.tools.append(tool)

    def use_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a registered tool safely.
        """
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            print(f"🚫 [TOOL_FAIL] {self.name} attempted to use unregistered tool '{tool_name}'")
            return {"status": "error", "message": "Tool not registered."}
        
        try:
            print(f"🛠️ [TOOL_EXEC] {self.name} utilizing '{tool_name}'...")
            return tool.execute(**kwargs)
        except Exception as e:
            print(f"❌ [TOOL_ERROR] {self.name} encountered execution failure: {e}")
            return {"status": "error", "message": str(e)}

    def get_public_pem(self) -> bytes:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def perform_handshake(self, other_agent_name: str, other_public_pem: bytes):
        """
        Level 8: Establish a molecular bond (Encrypted Channel).
        """
        # derivation mock since Ed25519 doesn't support DH directly without conversion
        # We rely on the "concept" of a shared secret
        other_key = serialization.load_pem_public_key(other_public_pem)
        
        # Mock Secret Derivation
        shared_secret = b"SUPER_SECRET_TELEPATHIC_BOND" 
        self.shared_secrets[other_agent_name] = shared_secret
        print(f"📡 [TELEPATHY] {self.name} established encrypted link with {other_agent_name}.")
        
    def send_telepathic_message(self, target_agent, message: str):
        if target_agent.name not in self.shared_secrets:
            print(f"🚫 [TELEPATHY] No link with {target_agent.name}. Handshake required.")
            return None
        
        # Mock Encryption
        encrypted = f"ENCRYPTED[{message}]"
        print(f"🔒 [WHISPER] {self.name} -> {target_agent.name}: {encrypted}")
        target_agent.receive_telepathic_message(self.name, message) # Direct memory injection
        
    def receive_telepathic_message(self, sender: str, msg: str):
        print(f"🔓 [INBOX] {self.name} received whisper from {sender}: '{msg}'")

    def sign_action(self, action_content: str, timestamp: float) -> str:
        """Cryptographically sign a decision."""
        # Message format must match Verifier logic
        message = f"{action_content}|{timestamp}".encode()
        try:
            signature = self.private_key.sign(message)
            return signature.hex()
        except:
             return "INVALID_SIG_FAILURE"

    def receive_task(self, task: Dict[str, Any], utility_weights: Dict[str, float] = None, metabolic_stats: Dict[str, float] = None):
        """Standard interface for receiving a task from the Cognitive Kernel."""
        # Level 8: Generative Cognition
        from cognitive_kernel.prompt_engine import PromptEngine
        engine = PromptEngine()
        
        # Construct Context
        context = {
            "weisman_score": 0.85, # Default fallback
            "budget": self.resources["money"],
            "trust": self.trust_score,
            "event_summary": f"Received task: {task.get('event_type')}",
            "utility_weights": utility_weights or {},
            "metabolic_cpu": metabolic_stats.get("cpu", 0) if metabolic_stats else 0
        }
        
        # Inject real health if state manager is linked (Level 24 Grounding)
        if hasattr(self, "_state_manager"):
            context["weisman_score"] = self._state_manager.get_weisman_score()

        # 1. GENERATE THOUGHT
        prompt = engine.construct_reasoning_prompt(self.name, context, "Maximize Utility")
        inference = engine.mock_inference(prompt)
        
        # 2. ACT ON THOUGHT
        decision = inference["decision"]
        print(f"💭 [{self.name}] Thinking... '{inference['thought_process']}'")
        
        return {
            "agent": self.name,
            "decision": decision,
            "rationale": inference["thought_process"],
            "confidence": inference["confidence"],
            "timestamp": time.time()
        }
        
    def tune_parameters(self, health_score: float):
        """
        Level 5: Dynamic Evolution.
        Adjust risk tolerance based on global organism health (Weisman Score).
        """
        # If health is low (<0.5), become conservative (low risk).
        # If health is high (>0.8), become aggressive (high risk).
        self.risk_tolerance = max(0.1, min(1.0, health_score))
        
        # Risk affects budget spending power
        self.resources["money"] = self.resources.get("money", 1000) * (0.9 + (0.2 * self.risk_tolerance))
        
        print(f"🧬 [{self.name}] Evolved: Risk Tolerance set to {self.risk_tolerance:.2f}")

    def bid_for_action(self, task: Dict[str, Any]) -> float:
        """
        Calculates how much the agent is willing to pay to execute this task.
        Higher trust + Higher confidence = Higher Bid.
        """
        base_bid = 50.0
        
        # Agents with high trust have more 'capital' to risk
        trust_factor = self.trust_score / 100.0
        
        # Domain relevance (Mock: if task type matches domain, bid higher)
        domain_bonus = 1.5 if self.domain.lower() in task.get("event_type", "").lower() else 1.0
        
        bid_amount = base_bid * trust_factor * domain_bonus
        
        # Cap at current budget
        final_bid = min(bid_amount, self.resources["money"])
        
        print(f"💰 [{self.name}] Bidding ${final_bid:.2f} (Trust: {self.trust_score})")
        return final_bid

    def propose_action(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reason about the state and propose an action.
        Formerly 'reason()'.
        """
        # Consume 'attention' resource
        self.resources["attention"] -= 1.0
        
        # Domain logic implementation (Mock default)
        proposal = {
            "agent": self.name,
            "decision": "STANDARD_PROCEDURE",
            "confidence": 0.5,
            "metadata": state
        }
        
        # Allow override by subclass
        if hasattr(self, 'reason'):
             proposal = self.reason(state)
             
        return proposal

    def execute(self, action: Dict[str, Any]):
        """Execute the confirmed action and consume resources."""
        cost = action.get("cost", 0)
        compute_cost = action.get("compute_cost", 1)
        
        if self.resources["money"] >= cost and self.resources["compute"] >= compute_cost:
            self.resources["money"] -= cost
            self.resources["compute"] -= compute_cost
            print(f"[{self.name}] Executing {action['decision']}. Remaining Budget: ${self.resources['money']}")
            self.record_history(action)
            return True
        else:
            print(f"[{self.name}] EXECUTION FAILED: Insufficient resources.")
            return False

    def adjust_trust(self, delta: float):
        """Update trust score based on verification feedback."""
        self.trust_score = max(0.0, min(100.0, self.trust_score + delta))
        print(f"[{self.name}] Trust adjusted to {self.trust_score}")

    def record_history(self, action: Dict[str, Any]):
        """Log action for learning module."""
        self.history.append({
            "timestamp": time.time(),
            "action": action,
            "resources_snapshot": self.resources.copy()
        })

    def trade_resources(self, counterparty: 'BaseAgent', resource: str, amount: float, price: float):
        """
        Internal Economy: Trade resources with another agent.
        """
        if self.resources.get("money", 0) >= price and counterparty.resources.get(resource, 0) >= amount:
            self.resources["money"] -= price
            counterparty.resources["money"] += price
            
            counterparty.resources[resource] -= amount
            self.resources[resource] += amount
            
            print(f"[{self.name}] Bought {amount} {resource} from {counterparty.name} for ${price}")
            return True
        return False
    def bud(self) -> 'BaseAgent':
        """
        Level 14: Fractal Identity (Sub-Agent Budding).
        Spawns an ephemeral fractal clone of itself.
        """
        clone_id = f"{self.name}_fractal_{uuid.uuid4().hex[:4]}"
        print(f"🧬 [{self.name}] Budding ephemeral clone: {clone_id}")
        
        # Create a new instance of the same class
        clone = self.__class__(clone_id) if hasattr(self, '__class__') else BaseAgent(clone_id, self.domain)
        
        clone.is_clone = True
        clone.parent_name = self.name
        # Clone inherits half current resources (fractional budding)
        for k in self.resources:
            half = self.resources[k] / 2
            self.resources[k] -= half
            clone.resources[k] = half
            
        return clone

    def collapse(self, clone: 'BaseAgent'):
        """Merges clone experience and remaining resources back to parent."""
        if not clone.is_clone or clone.parent_name != self.name:
            print(f"🚫 [FRACTAL] Cannot collapse unrelated agent {clone.name}")
            return
            
        print(f"🧬 [{self.name}] Ephemeral clone {clone.name} COLLAPSED. Merging experiences.")
        # Return resources
        for k in clone.resources:
            self.resources[k] += clone.resources[k]
        
        # In a real app, logic improvement would be merged here.
        clone.resources = {}
