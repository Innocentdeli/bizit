import hashlib
import time
import random
from typing import Dict, Any
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

class Verifier:
    """
    Level 6-11: Trust Layer.
    Manages cryptographic identity registration and action verification.
    """
    def __init__(self):
        self.trust_scores = {}
        # Registry of agent public keys
        self.public_keys = {} 

    def register_agent(self, agent_name: str, public_key_pem: bytes):
        """Register an agent's public key for signature verification."""
        try:
            public_key = serialization.load_pem_public_key(public_key_pem)
            self.public_keys[agent_name] = public_key
            print(f"[TRUST] Registered Identity for {agent_name}")
        except Exception as e:
            print(f"[TRUST] FAILED Identity Registration for {agent_name}: {e}")

    def verify_action(self, action_data: Dict[str, Any], signature_hex: str) -> bool:
        """
        Verify business actions using Ed25519 Cryptography.
        """
        agent_id = action_data.get("agent", "unknown")
        decision = action_data.get("decision")
        
        # 1. Check Identity Registration
        if agent_id not in self.public_keys:
             # print(f"[TRUST] FAILED: Unknown Identity {agent_id}. Cannot verify signature.")
             return False

        # 2. Reconstruct the message that was signed
        timestamp = action_data.get("timestamp_signature_basis", 0)
        message = f"{decision}|{timestamp}".encode()
        
        try:
            signature = bytes.fromhex(signature_hex)
            public_key = self.public_keys[agent_id]
            public_key.verify(signature, message)
            
            # Reward
            self.adjust_trust_score(agent_id, +0.01)
            return True
            
        except Exception as e:
             print(f"[TRUST] INVALID SIGNATURE for {agent_id}: {e}")
             self.adjust_trust_score(agent_id, -0.05)
             return False
    
    def calculate_trust_score(self, agent_id: str) -> float:
        """Get current trust score."""
        return self.trust_scores.get(agent_id, 0.98) # Start high

    def adjust_trust_score(self, agent_id: str, delta: float):
        current = self.trust_scores.get(agent_id, 0.98)
        new_score = max(0.0, min(1.0, current + delta))
        self.trust_scores[agent_id] = new_score
        
        if abs(new_score - current) > 0.1: # Only print significant shifts to reduce console noise
             print(f"[TRUST] Agent {agent_id} Trust updated: {current:.2f} -> {new_score:.2f}")

    def generate_proof(self, action_data: Dict[str, Any]) -> str:
        """Deprecated: Use Agents.sign_action directly."""
        return "Legacy Proof: Use Ed25519"
