import socket
import threading
import time
import json

class MyceliumNetwork:
    """
    Level 10: Network Mycelium (P2P Mesh).
    Allows BIZIT instances to discover each other via UDP Broadcast.
    """
    def __init__(self, agent_name="BIZIT_NODE", port=5005):
        self.agent_name = agent_name
        self.port = port
        self.peers = {} # {ip: {last_seen, name}}
        self.running = True
        
        # UDP Socket for Broadcasting
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
             self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
             pass 
        self.sock.bind(("", self.port))
        self.callbacks = {} # {type: func}
        
        # Start Threads
        threading.Thread(target=self.listen, daemon=True).start()
        threading.Thread(target=self.broadcast_presence, daemon=True).start()
        
    def register_callback(self, msg_type: str, func):
        self.callbacks[msg_type] = func

    def send_message(self, msg_dict: dict, target_ip=None):
        """Send a generic message over the mesh."""
        message = json.dumps({
            **msg_dict,
            "sender": self.agent_name,
            "timestamp": time.time()
        })
        try:
            target = target_ip if target_ip else '<broadcast>'
            self.sock.sendto(message.encode(), (target, self.port))
        except Exception as e:
            print(f"🍄 [MYCELIUM] Send failed: {e}")

    def broadcast_presence(self):
        while self.running:
            self.send_message({"type": "HELLO"})
            time.sleep(5) # Pulse every 5 seconds

    def listen(self):
        print(f"🍄 [MYCELIUM] Listening on port {self.port}...")
        while self.running:
            try:
                data, addr = self.sock.recvfrom(2048) # Increased buffer
                message = json.loads(data.decode())
                
                sender = message.get('sender', 'unknown')
                msg_type = message.get('type')

                if sender != self.agent_name: # Don't talk to self
                    if msg_type in ["CONSENSUS_PROPOSAL", "CONSENSUS_VOTE"]:
                        print(f"🍄 [MYCELIUM] Swarm Activity Detected: {msg_type} from {sender}")
                    
                    if addr[0] not in self.peers:
                        print(f"🍄 [MYCELIUM] New Node Discovered: {sender} at {addr[0]}")
                    
                    self.peers[addr[0]] = {
                        "name": sender,
                        "last_seen": time.time()
                    }

                    # Trigger Callbacks
                    if msg_type in self.callbacks:
                        self.callbacks[msg_type](message, addr[0])

            except Exception as e:
                pass

    def get_active_peers(self):
        # Prune old peers (> 10s)
        now = time.time()
        active = {ip: p for ip, p in self.peers.items() if now - p['last_seen'] < 15}
        self.peers = active
        return active
