from typing import List, Dict, Any
import json
import uuid

def json_default(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def safe_dumps(data):
    return json.dumps(data, default=json_default)
import os
import time

try:
    import redis
    _REDIS_AVAILABLE = True
except ImportError:
    _REDIS_AVAILABLE = False

class OrganismState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OrganismState, cls).__new__(cls)
            cls._instance._init_storage()
        return cls._instance

    def _init_storage(self):
        self.use_redis = _REDIS_AVAILABLE and os.getenv("USE_REDIS", "false").lower() == "true"
        if self.use_redis:
            try:
                self.r = redis.Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", 6379)),
                    decode_responses=True
                )
                self.r.ping()
                print("[STATE] Connected to Redis Backend.")
            except Exception as e:
                print(f"[STATE] Redis connection failed ({e}). Falling back to memory.")
                self.use_redis = False
        
        # In-memory fallback
        self.memory_events = []
        self.memory_actions = []
        self.memory_ledger = []
        self.status_message = "Initializing..."
        self.automation_enabled = {
            "REORDER_INVENTORY": True,
            "OPTIMIZE_PRICING": True,
            "ROUTING_LOGISTICS": True,
            "EXECUTE_TRADE": True,
            "CLOSE_POSITION": True,
            "EXECUTE_DEFI_TRADE": True,
            "CLOSE_DEFI_POSITION": True
        }
        self.memory_notifications = []
        self.memory_board_minutes = []
        self.memory_documents = [] # Document Ingestion Store
        self.memory_persona = {
            "hq": "Lagos, Nigeria",
            "primary_currency": "NGN",
            "risk_profile": "MODERATE",
            "growth_goals": ["Market Expansion", "Supply Chain Resilience"],
            "sector": "General Retail"
        }
        self.memory_feedbacks = [] # Outcome Verification History
        self.weisman_base = 0.85
        self.weisman_history = []
        self.agent_trust_history = {} # { "finance": [98, 97, 98], ... }
        
        # Level 33: Financial Vitals (Grounding)
        self.financial_vitals = {
            "shopify": {"total_sales_24h": 0, "order_count": 0},
            "stripe": {"available_balance": 0},
            "oanda": {"balance": 0, "pnl": 0, "currency": "USD", "instruments": []},
            "quickbooks": {"total_revenue": 0, "active_invoices": 0},
            "plaid": {"total_bank_balance": 0, "account_count": 0},
            "last_updated": 0
        }
        self.market_quotes = {} # { "EUR_USD": {"bid": 1.05, "ask": 1.06, "avg": 1.055} }
        self.defi_vitals = {
            "usdc_balance": 10000.0,
            "gas_eth": 0.5,
            "net_pnl": 0.0,
            "active_positions": []
        }
        self.defi_quotes = {} # { "BTC_USD": 95000, "ETH_USD": 2500 }
        self.sov_balance = 1000.0 # Initial BIZIT_SOV reserve
        self.treasury_ledger = [] # Autonomous inter-node taxation history
        self.metabolic_stats = {"cpu": 0, "ram": 0} # Level 33
        self.consensus_data = {"agreement": 0.0, "voters": 0, "active_proposal": None} # Level 34
        self.active_directives = [] # Level 27: Sovereign God Mode
        
        # Persistence (Level 6)
        self.load_state()

    def get_snapshot(self) -> Dict[str, Any]:
        """Level 24: High-fidelity snapshot for DigitalTwin cloning."""
        return {
            "sov_balance": self.sov_balance,
            "defi_vitals": self.defi_vitals,
            "defi_quotes": self.defi_quotes,
            "financial_vitals": self.financial_vitals,
            "market_quotes": self.market_quotes,
            "timestamp": time.time()
        }

    def save_state(self):
        """Persist memory to disk (Level 24: Cross-Process Sync Fallback)."""
        if self.use_redis: return 
        
        state_dump = {
            "weisman_history": self.weisman_history,
            "agent_trust_history": self.agent_trust_history,
            "board_minutes": self.memory_board_minutes,
            "notifications": self.memory_notifications,
            "automation": self.automation_enabled,
            "events": self.memory_events,
            "actions": self.memory_actions,
            "ledger": self.memory_ledger,
            "financial_vitals": self.financial_vitals,
            "sov_balance": self.sov_balance,
            "treasury_ledger": self.treasury_ledger,
            "defi_quotes": self.defi_quotes,
            "market_quotes": self.market_quotes,
            "metabolic_stats": self.metabolic_stats,
            "consensus_data": self.consensus_data,
            "active_directives": self.active_directives,
            "documents": self.memory_documents,
            "persona": self.memory_persona,
            "feedbacks": self.memory_feedbacks
        }
        try:
            # Atomic write
            tmp_file = "organism_state.json.tmp"
            with open(tmp_file, "w") as f:
                json.dump(state_dump, f, default=json_default)
            os.replace(tmp_file, "organism_state.json")
        except Exception as e:
            print(f"[STATE] Save failed: {e}")

    def load_state(self):
        """Restore memory from disk (Level 24: Cross-Process Sync Fallback)."""
        if self.use_redis: return
        
        if os.path.exists("organism_state.json"):
            try:
                with open("organism_state.json", "r") as f:
                    data = json.load(f)
                    self.weisman_history = data.get("weisman_history", [])
                    self.agent_trust_history = data.get("agent_trust_history", {})
                    self.memory_board_minutes = data.get("board_minutes", [])
                    self.memory_notifications = data.get("notifications", [])
                    self.automation_enabled = data.get("automation", self.automation_enabled)
                    self.memory_events = data.get("events", [])
                    self.memory_actions = data.get("actions", [])
                    self.memory_ledger = data.get("ledger", [])
                    self.financial_vitals = data.get("financial_vitals", self.financial_vitals)
                    self.sov_balance = data.get("sov_balance", self.sov_balance)
                    self.treasury_ledger = data.get("treasury_ledger", [])
                    self.defi_quotes = data.get("defi_quotes", {})
                    self.market_quotes = data.get("market_quotes", {})
                    self.metabolic_stats = data.get("metabolic_stats", {"cpu": 0, "ram": 0})
                    self.consensus_data = data.get("consensus_data", {"agreement": 0.0, "voters": 0, "active_proposal": None})
                    self.active_directives = data.get("active_directives", [])
                    self.memory_documents = data.get("documents", [])
                    self.memory_persona = data.get("persona", self.memory_persona)
                    self.memory_feedbacks = data.get("feedbacks", [])
                # print("[STATE] Memory Restored from Disk.")
            except Exception as e:
                pass # Silently fail on corruption during concurrent access

    def record_snapshot(self, agent_fleet_trust: Dict[str, float]):
        """Records a point in time for Weisman and Trust scores."""
        timestamp = time.time()
        current_weisman = self.get_weisman_score()
        
        # Record Weisman
        entry = {"timestamp": timestamp, "score": current_weisman}
        if self.use_redis:
            self.r.lpush("bizit:weisman_history", safe_dumps(entry))
            self.r.ltrim("bizit:weisman_history", 0, 49) # Keep last 50
        else:
            self.weisman_history.append(entry)
            if len(self.weisman_history) > 50: self.weisman_history.pop(0)
            
        # Record Agent Trust
        for name, score in agent_fleet_trust.items():
            t_entry = {"timestamp": timestamp, "score": score}
            if self.use_redis:
                self.r.lpush(f"bizit:trust_history:{name}", safe_dumps(t_entry))
                self.r.ltrim(f"bizit:trust_history:{name}", 0, 49)
            else:
                if name not in self.agent_trust_history: self.agent_trust_history[name] = []
                self.agent_trust_history[name].append(t_entry)
                if len(self.agent_trust_history[name]) > 50: self.agent_trust_history[name].pop(0)

    @property
    def trends(self):
        """Returns the history for visualization."""
        if self.use_redis:
            # We would pull from Redis here
            return {} 
        return {
            "weisman": self.weisman_history,
            "trust": self.agent_trust_history
        }

    def add_board_minutes(self, minutes: Dict[str, Any]):
        if self.use_redis:
            self.r.lpush("bizit:board_minutes", safe_dumps(minutes))
            self.r.ltrim("bizit:board_minutes", 0, 9) # Keep last 10 meetings
        else:
            self.memory_board_minutes.insert(0, minutes)
            if len(self.memory_board_minutes) > 10: self.memory_board_minutes.pop()

    @property
    def board_minutes(self):
        if self.use_redis:
            raw = self.r.lrange("bizit:board_minutes", 0, -1)
            return [json.loads(x) for x in raw]
        return self.memory_board_minutes

    def add_document(self, doc_data: Dict[str, Any]):
        if self.use_redis:
            self.r.lpush("bizit:documents", safe_dumps(doc_data))
            self.r.ltrim("bizit:documents", 0, 49) # Keep last 50 docs
        else:
            self.memory_documents.insert(0, doc_data)
            if len(self.memory_documents) > 50: self.memory_documents.pop()
        self.save_state()

    @property
    def documents(self):
        if self.use_redis:
            raw = self.r.lrange("bizit:documents", 0, -1)
            return [json.loads(x) for x in raw]
        return self.memory_documents

    def update_persona(self, persona_data: Dict[str, Any]):
        self.memory_persona.update(persona_data)
        if self.use_redis:
            self.r.set("bizit:persona", safe_dumps(self.memory_persona))
        self.save_state()

    @property
    def persona(self):
        if self.use_redis:
            raw = self.r.get("bizit:persona")
            return json.loads(raw) if raw else self.memory_persona
        return self.memory_persona

    def add_feedback(self, feedback: Dict[str, Any]):
        if self.use_redis:
            self.r.lpush("bizit:feedbacks", safe_dumps(feedback))
            self.r.ltrim("bizit:feedbacks", 0, 99)
        else:
            self.memory_feedbacks.insert(0, feedback)
            if len(self.memory_feedbacks) > 100: self.memory_feedbacks.pop()
        self.save_state()

    @property
    def feedbacks(self):
        if self.use_redis:
            raw = self.r.lrange("bizit:feedbacks", 0, -1)
            return [json.loads(x) for x in raw]
        return self.memory_feedbacks

    def add_notification(self, level: str, message: str, category: str):
        """Levels: info, warning, risk, goal, anomaly"""
        note = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
            "category": category
        }
        if self.use_redis:
            self.r.lpush("bizit:notifications", safe_dumps(note))
            self.r.ltrim("bizit:notifications", 0, 19) # Keep last 20
        else:
            self.memory_notifications.insert(0, note)
            if len(self.memory_notifications) > 20: self.memory_notifications.pop()

    @property
    def notifications(self):
        if self.use_redis:
            raw = self.r.lrange("bizit:notifications", 0, -1)
            return [json.loads(x) for x in raw]
        return self.memory_notifications

    def get_weisman_score(self) -> float:
        """
        The Weisman Score is derived from the moving average of realized utility
        relative to the 0.85 base.
        """
        actions = self.agent_actions
        if not actions:
            return self.weisman_base
            
        # Extract utility from last 10 successful actions
        utilities = [
            a.get("realized_utility", 0.5) 
            for a in actions[:10] 
            if a.get("status") in ["SUCCESS", "AUTOMATED"]
        ]
        
        if not utilities:
            return self.weisman_base
            
        avg_utility = sum(utilities) / len(utilities)
        # Scale to 0-1 range around the base
        normalized = 0.85 + (avg_utility/10000 * 0.1) 
        return min(0.99, max(0.1, normalized))

    def set_automation(self, key: str, enabled: bool):
        self.automation_enabled[key] = enabled
        if self.use_redis:
            self.r.hset("bizit:automation", key, str(enabled))

    def is_automated(self, key: str) -> bool:
        # Level 51: Auto-execute Alpha signals
        if key.startswith("EXECUTE_PATERNAL") or "ALPHA" in key:
            return True
            
        if self.use_redis:
            val = self.r.hget("bizit:automation", key)
            return val.lower() == "true" if val else self.automation_enabled.get(key, False)
        return self.automation_enabled.get(key, False)

    def update_status(self, msg: str):
        self.status_message = msg
        if self.use_redis:
            self.r.set("bizit:status", msg)

    def update_metabolic_stats(self, data: dict):
        """Level 33: Track host system health for utility penalties."""
        self.metabolic_stats = data
        if self.use_redis:
            from models.events import safe_dumps
            self.r.set("bizit:metabolic", safe_dumps(data))
        # print(f"🧬 [STATE] Metabolic Stats updated: CPU {data['cpu']}%")

    def update_consensus_stats(self, data: dict):
        """Level 34: Track P2P swarm consensus for UI visualization."""
        self.consensus_data.update(data)
        if self.use_redis:
            from models.events import safe_dumps
            self.r.set("bizit:consensus", safe_dumps(self.consensus_data))
        self.save_state()

    def update_financial_vitals(self, source: str, data: dict):
        """Level 33: Link real-world economic flows to the organism."""
        if source in self.financial_vitals:
            self.financial_vitals[source].update(data)
            self.financial_vitals["last_updated"] = time.time()
            if self.use_redis:
                # Use safe_dumps or direct redis hash set
                from models.events import safe_dumps
                self.r.set(f"bizit:finance:{source}", safe_dumps(self.financial_vitals[source]))
            print(f"💰 [STATE] Financial Vitals updated from {source.upper()}")
            self.save_state()

    def update_market_quote(self, pair: str, data: dict):
        """Level 37: Track live market prices for active trading."""
        self.market_quotes[pair] = data
        if self.use_redis:
            from models.events import safe_dumps
            self.r.set(f"bizit:market:{pair}", safe_dumps(data))
        print(f"📈 [STATE] Market Quote updated: {pair} @ {data.get('bid')}/{data.get('ask')}")
        self.save_state()

    def update_defi_vitals(self, data: dict):
        """Tier 7: Track on-chain collateral and gas energy."""
        self.defi_vitals.update(data)
        if self.use_redis:
            from models.events import safe_dumps
            self.r.set("bizit:defi_vitals", safe_dumps(self.defi_vitals))
        print(f"⛓️ [STATE] DeFi Vitals updated: USDC Balance: ${self.defi_vitals['usdc_balance']:.2f}")
        self.save_state()

    def update_defi_quote(self, pair: str, price: float):
        """Tier 7: Track on-chain DEX/Synthetic prices."""
        self.defi_quotes[pair] = price
        if self.use_redis:
            self.r.hset("bizit:defi_quotes", pair, str(price))
        print(f"💎 [STATE] DeFi Quote updated: {pair} @ ${price:,.2f}")
        self.save_state()

    def mint_sov(self, amount: float, reason: str):
        """Level 23: Issue new BIZIT_SOV currency based on organic productivity."""
        self.sov_balance += amount
        self.add_ledger_entry({
            "type": "MINT",
            "currency": "BIZIT_SOV",
            "amount": amount,
            "reason": reason,
            "timestamp": time.time()
        })
        if self.use_redis:
            self.r.set("bizit:currency:sov", str(self.sov_balance))
        print(f"🏦 [SOVEREIGN] Minted {amount:.2f} SOV. Total: {self.sov_balance:.2f} SOV")
        self.save_state()

    def collect_tax(self, amount: float, source: str):
        """Level 23: Autonomous inter-node taxation protocol."""
        self.sov_balance += amount
        entry = {
            "type": "TAX",
            "source": source,
            "amount": amount,
            "timestamp": time.time()
        }
        self.treasury_ledger.append(entry)
        if self.use_redis:
            self.r.lpush("bizit:treasury:ledger", safe_dumps(entry))
            self.r.set("bizit:currency:sov", str(self.sov_balance))
        print(f"📜 [SOVEREIGN] Tax Collected: {amount:.2f} SOV from {source}")
        self.save_state()

    def add_event(self, event: Dict[str, Any]):
        data = safe_dumps(event)
        if self.use_redis:
            self.r.lpush("bizit:events", data)
            self.r.ltrim("bizit:events", 0, 99) # Keep last 100
        else:
            self.memory_events.append(event)
            if len(self.memory_events) > 50: self.memory_events.pop(0)
            self.save_state()

    def add_action(self, action: Dict[str, Any]):
        data = safe_dumps(action)
        if self.use_redis:
            self.r.lpush("bizit:actions", data)
            self.r.ltrim("bizit:actions", 0, 99)
        else:
            self.memory_actions.append(action)
            if len(self.memory_actions) > 50: self.memory_actions.pop(0)
            self.save_state()
    
    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """Get document by ID."""
        return next((d for d in self.memory_documents if d.get("id") == doc_id), None)

    def add_ledger_entry(self, entry: Dict[str, Any]):
        data = safe_dumps(entry)
        if self.use_redis:
            self.r.lpush("bizit:ledger", data)
            self.r.ltrim("bizit:ledger", 0, 99)
        else:
            self.memory_ledger.append(entry)

    @property
    def events(self):
        if self.use_redis:
            raw = self.r.lrange("bizit:events", 0, -1)
            return [json.loads(x) for x in raw]
        return self.memory_events

    @property
    def trust_ledger(self):
        if self.use_redis:
            raw = self.r.lrange("bizit:ledger", 0, -1)
            return [json.loads(x) for x in raw]
        return self.memory_ledger

    @property
    def agent_actions(self):
        if self.use_redis:
            raw = self.r.lrange("bizit:actions", 0, -1)
            return [json.loads(x) for x in raw]
        return self.memory_actions

    def get_dynamic_state(self) -> Dict[str, Any]:
        """Level 70: Returns a synthesized 'Business Twin' state for dynamic grounding."""
        return {
            "persona": self.persona,
            "vitals": {
                "liquid_cash": self.financial_vitals.get("stripe", {}).get("available_balance", 0) + 
                               self.financial_vitals.get("plaid", {}).get("total_bank_balance", 0),
                "recent_sales_24h": self.financial_vitals.get("shopify", {}).get("total_sales_24h", 0),
                "active_invoices": self.financial_vitals.get("quickbooks", {}).get("active_invoices", 0)
            },
            "market": self.market_quotes.get(f"{self.persona.get('primary_currency', 'USD')}_USD", {}),
            "weisman": self.get_weisman_score(),
            "timestamp": time.time()
        }

    def get_summary(self):
        return {
            "organism_status": self.r.get("bizit:status") if self.use_redis else self.status_message,
            "event_count": len(self.events),
            "action_count": len(self.agent_actions),
            "ledger_depth": len(self.trust_ledger),
            "weisman_score": self.get_weisman_score()
        }
