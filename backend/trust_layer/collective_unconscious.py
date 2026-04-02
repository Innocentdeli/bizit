class CollectiveUnconscious:
    """
    Level 16: Synthetic Collective Unconscious.
    Enables nodes to share compressed 'Intuition Matrices' and 'Wisdom Leaks' across the Mycelium mesh.
    """
    def __init__(self, mycelium, state_manager):
        self.mycelium = mycelium
        self.state_manager = state_manager
        self.intuition_pool = {} # {agent_domain: [list of weight vectors]}
        
        # Register callback for Mycelium leaks
        self.mycelium.register_callback("INTUITION_LEAK", self.handle_leak)

    def handle_leak(self, message, addr):
        """
        P2P Callback: Absorbs wisdom from another node.
        """
        self.absorb_leak(message)

    def broadcast_intuition(self, domain, weights):
        """
        Pushes a successful intuition pattern to the collective mesh.
        """
        packet = {
            "type": "INTUITION_LEAK",
            "domain": domain,
            "weights": weights,
            "source_weisman": self.state_manager.get_weisman_score()
        }
        self.mycelium.send_message(packet)
        print(f"🌌 [UNCONSCIOUS] Leaking {domain} intuition to the collective (Source Weisman: {packet['source_weisman']:.4f})")

    def absorb_leak(self, packet):
        """
        Integrates peer wisdom into the local intuition pool.
        """
        domain = packet.get("domain")
        weights = packet.get("weights")
        if domain not in self.intuition_pool:
            self.intuition_pool[domain] = []
            
        self.intuition_pool[domain].append(weights)
        print(f"🧠 [UNCONSCIOUS] Absorbed Collective Wisdom for {domain} from Mycelium mesh.")

    def get_collective_bias(self, domain):
        """
        Returns the latest collective intuition for a domain.
        """
        patterns = self.intuition_pool.get(domain, [])
        if not patterns:
            return None
        return patterns[-1] # Return the most recent 'leak'
