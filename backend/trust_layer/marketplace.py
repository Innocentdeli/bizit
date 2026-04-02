import time
from typing import Dict, Any, List

class ResourceMarketplace:
    """
    Level 12: Sovereign Protocol (P2P Marketplace).
    Enables BIZIT instances to trade computing and business resources over the mesh.
    """
    def __init__(self, mycelium, state_manager):
        self.mycelium = mycelium
        self.state_manager = state_manager
        self.active_offers = [] 
        self.active_requests = []
        
        # Register Mycelium Callbacks
        self.mycelium.register_callback("RESOURCE_OFFER", self._handle_offer)
        self.mycelium.register_callback("RESOURCE_REQUEST", self._handle_request)
        self.mycelium.register_callback("TRADE_PROPOSAL", self._handle_trade_proposal)

    def broadcast_offer(self, resource: str, amount: float, price: float):
        """Publicly broadcast that we have surplus resources."""
        print(f"[MARKET] Offering {amount} {resource} at ${price}")
        self.mycelium.send_message({
            "type": "RESOURCE_OFFER",
            "resource": resource,
            "amount": amount,
            "price": price
        })

    def broadcast_request(self, resource: str, amount: float):
        """Publicly broadcast that we are resource-deficient."""
        print(f"[MARKET] Requesting {amount} {resource}")
        self.mycelium.send_message({
            "type": "RESOURCE_REQUEST",
            "resource": resource,
            "amount": amount
        })

    def propose_trade(self, target_node_ip: str, resource: str, amount: float, price: float):
        """Directly propose a trade to a specific peer."""
        print(f"[MARKET] Proposing Trade to {target_node_ip}: {amount} {resource} for ${price}")
        self.mycelium.send_message({
            "type": "TRADE_PROPOSAL",
            "resource": resource,
            "amount": amount,
            "price": price
        }, target_ip=target_node_ip)

    def _handle_offer(self, message: dict, sender_ip: str):
        print(f"[MARKET] Remote Offer: {message['sender']} has {message['amount']} {message['resource']} for ${message['price']}")
        self.active_offers.append({**message, "ip": sender_ip})
        # Prune old
        self.active_offers = self.active_offers[-20:]

    def _handle_request(self, message: dict, sender_ip: str):
        print(f"[MARKET] Remote Request: {message['sender']} needs {message['amount']} {message['resource']}")
        self.active_requests.append({**message, "ip": sender_ip})
        self.active_requests = self.active_requests[-20:]

    def _handle_trade_proposal(self, message: dict, sender_ip: str):
        """
        Level 12: Settlement Logic.
        Accepts trade if parameters are rational.
        """
        print(f"[MARKET] Trade Proposal from {message['sender']} for {message['resource']}")
        # Rational check (Mock)
        if message['price'] < 1000: # Threshold for auto-accept
             print(f"[MARKET] Rational Trade Detected. Accepting from {message['sender']}...")
             self.mycelium.send_message({
                 "type": "TRADE_ACCEPT",
                 "resource": message['resource'],
                 "amount": message['amount'],
                 "price": message['price']
             }, target_ip=sender_ip)
