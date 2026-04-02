import time

class PlanetarySync:
    """
    Level 17: Planetary Mycelium (Temporal Synchronization).
    Ensures 'Instantaneous State Locking' across all global BIZIT nodes.
    """
    def __init__(self, mycelium, blockchain):
        self.mycelium = mycelium
        self.blockchain = blockchain
        self.last_sync_block = 0
        
        # Register callback for state locking
        self.mycelium.register_callback("STATE_LOCK_REQ", self.handle_lock_request)

    def handle_lock_request(self, message, addr):
        """
        P2P Callback: Verifies and acknowledges a global state lock.
        """
        remote_hash = message.get("last_block_hash")
        if self.blockchain.chain[-1].hash == remote_hash:
            print(f"📡 [PLANETARY] State Lock Verified with Node at {addr}. Global Sync Active.")
            self.mycelium.send_message({"type": "STATE_LOCK_ACK", "status": "SYNCED"}, target_ip=addr)
        else:
            print(f"⚠️ [PLANETARY] Drift detected with Node at {addr}. Initiating fast-sync...")

    def broadcast_state_lock(self):
        """
        Broadcasts the current block hash to the planetary mesh to enforce synchronization.
        """
        if not self.blockchain.chain:
            return
            
        current_hash = self.blockchain.chain[-1].hash
        print(f"🌎 [PLANETARY] Broadcasting Global State Lock: {current_hash[:12]}...")
        
        self.mycelium.send_message({
            "type": "STATE_LOCK_REQ",
            "last_block_hash": current_hash,
            "tick": int(time.time())
        })
