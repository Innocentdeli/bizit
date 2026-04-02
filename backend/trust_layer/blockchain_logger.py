import hashlib
import json
import time
from typing import Dict, Any

class BlockchainLogger:
    def __init__(self):
        self.chain = []
        self._initialize_chain()

    def _initialize_chain(self):
        # Genesis block
        self.chain.append({
            "index": 0,
            "timestamp": time.time(),
            "data": "BIZIT GENESIS BLOCK",
            "previous_hash": "0",
            "hash": "BIZIT_ROOT_TRUST_ANCHOR"
        })

    def log_action(self, action_data: Dict[str, Any], proof: str):
        """Logs a verified action to the immutable ledger."""
        prev_block = self.chain[-1]
        
        block = {
            "index": len(self.chain),
            "timestamp": time.time(),
            "action": action_data,
            "proof": proof,
            "validator_signature": f"SIG-BIZIT-V1-{int(time.time())}", # Simulated Validator Sig
            "previous_hash": prev_block["hash"]
        }
        
        # Proof of Work / Hashing
        block["hash"] = self._calculate_hash(block)
        self.chain.append(block)
        
        # Write to disk/db (Simulated persistence)
        # In T3 this would be an L2 chain commit
        print(f"[TRUST] Block #{block['index']} committed to ledger. Hash: {block['hash'][:10]}...")

    def _calculate_hash(self, block: Dict[str, Any]) -> str:
        # Create a copy without 'hash' to ensure consistent calculation
        block_string = json.dumps({k:v for k,v in block.items() if k!='hash'}, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def get_ledger(self):
        return self.chain
