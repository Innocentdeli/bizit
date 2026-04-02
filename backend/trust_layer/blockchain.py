import hashlib
import json
import time
from typing import List, Dict, Any

class Block:
    def __init__(self, index: int, timestamp: float, data: Dict[str, Any], previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        # Sort keys to ensure consistent hashing
        block_string = json.dumps(self.data, sort_keys=True) + str(self.index) + str(self.timestamp) + self.previous_hash
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    """
    Level 9: The Immutable Chain.
    A tamper-evident ledger of all Organism actions.
    """
    def __init__(self):
        self.chain: List[Block] = [self.create_genesis_block()]

    def create_genesis_block(self) -> Block:
        return Block(0, time.time(), {"message": "GENESIS_BLOCK_BIZIT_V1"}, "0")

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, data: Dict[str, Any]) -> Block:
        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=latest_block.hash
        )
        self.chain.append(new_block)
        print(f"⛓️ [CHAIN] New Block #{new_block.index} Mined. Hash: {new_block.hash[:8]}...")
        return new_block

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                print(f"❌ [CHAIN] Invalid Hash at Block #{current_block.index}")
                return False

            if current_block.previous_hash != previous_block.hash:
                print(f"❌ [CHAIN] Broken Link at Block #{current_block.index}")
                return False
        return True
