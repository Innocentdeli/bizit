import asyncio
import json
import logging
import websockets
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class DerivClient:
    """
    Level 48: Deriv API Client.
    Uses WebSockets for real-time data and low-latency execution.
    """
    
    def __init__(self, token: str, app_id: str = "1"):
        self.token = token
        self.app_id = app_id
        self.ws_url = f"wss://ws.binaryws.com/websockets/v3?app_id={self.app_id}"
        self.ws = None
        self._authorized = False
        
    async def connect(self):
        """ESTABLISH SECURE WS LINK"""
        is_open = False
        try:
            is_open = self.ws is not None and getattr(self.ws, 'open', False)
        except Exception:
            pass
            
        if is_open:
            return
        
        try:
            self.ws = await websockets.connect(self.ws_url, ping_interval=20, ping_timeout=10)
            self._authorized = False
            logger.info("Deriv WS Connected.")
        except Exception as e:
            logger.error(f"Deriv Connection Failed: {e}")
            self.ws = None
            
    async def is_alive(self) -> bool:
        """CHECK WS METABOLISM"""
        try:
            return self.ws is not None and getattr(self.ws, 'open', False) and self._authorized
        except Exception:
            return False

    async def ensure_connection(self):
        """MAINTAIN PATERNAL LINK"""
        if not await self.is_alive():
            logger.info("Deriv Link Lost. Re-establishing...")
            await self.connect()
            await self.authorize()

    async def authorize(self) -> bool:
        """AUTH WITH PATERNAL TOKEN"""
        is_open = False
        try:
            is_open = self.ws is not None and getattr(self.ws, 'open', False)
        except Exception:
            pass
            
        if not is_open:
            await self.connect()
        
        if not self.ws:
            return False

        auth_req = {"authorize": self.token}
        await self.ws.send(json.dumps(auth_req))
        
        resp = await self.ws.recv()
        data = json.loads(resp)
        
        if "error" in data:
            logger.error(f"Deriv Auth Failed: {data['error']['message']}")
            self._authorized = False
            return False
        
        self._authorized = True
        logger.info(f"Deriv Authorized: {data['authorize']['fullname']}")
        return True

    async def get_candles(self, symbol: str, granularity: int = 3600, count: int = 100) -> List[Dict]:
        """Fetch historical candles with auto-reconnect."""
        await self.ensure_connection()
            
        req = {
            "ticks_history": symbol,
            "end": "latest",
            "style": "candles",
            "count": count,
            "granularity": granularity
        }
        
        try:
            await self.ws.send(json.dumps(req))
            resp = await self.ws.recv()
            data = json.loads(resp)
            
            if "error" in data:
                logger.error(f"Deriv Candle Fetch Failed: {data['error']['message']}")
                return []
                
            candles = []
            for tick in data.get("candles", []):
                candles.append({
                    "time": tick["epoch"],
                    "open": float(tick["open"]),
                    "high": float(tick["high"]),
                    "low": float(tick["low"]),
                    "close": float(tick["close"]),
                    "volume": 0
                })
            return candles
        except Exception as e:
            logger.error(f"Deriv Request Error: {e}")
            return []

    async def get_live_quotes(self, symbol: str) -> Dict:
        """Fetch latest tick for a symbol."""
        if not self._authorized:
            await self.authorize()

        req = {"ticks": symbol}
        await self.ws.send(json.dumps(req))
        resp = await self.ws.recv()
        data = json.loads(resp)
        
        if "error" in data:
            return {}
            
        return {
            "bid": float(data["tick"]["bid"]),
            "ask": float(data["tick"]["ask"]),
            "price": float(data["tick"]["quote"]),
            "timestamp": data["tick"]["epoch"]
        }

    async def place_order(self, symbol: str, side: str, amount: float, stop_loss: float):
        """Place a Deriv trade with re-auth check."""
        await self.ensure_connection()
            
        contract_type = "CALL" if side == "BUY" else "PUT"
        
        req = {
            "buy": "1",
            "price": amount,
            "parameters": {
                "amount": amount,
                "basis": "stake",
                "contract_type": contract_type,
                "currency": "USD",
                "duration": 1,
                "duration_unit": "h",
                "symbol": symbol
            }
        }
        
        try:
            await self.ws.send(json.dumps(req))
            resp = await self.ws.recv()
            data = json.loads(resp)
            
            if "error" in data:
                return {"error": data["error"]["message"]}
                
            return {
                "status": "SUCCESS",
                "contract_id": data["buy"]["contract_id"],
                "purchase_time": data["buy"]["purchase_time"]
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_account_summary(self) -> Dict:
        """Fetch balance and account info with re-auth."""
        await self.ensure_connection()
        
        req = {"balance": 1}
        try:
            await self.ws.send(json.dumps(req))
            resp = await self.ws.recv()
            data = json.loads(resp)
            
            if "error" in data:
                return {}
                
            return {
                "balance": float(data["balance"]["balance"]),
                "currency": data["balance"]["currency"],
                "unrealized_pl": 0,
                "margin_used": 0,
                "margin_available": float(data["balance"]["balance"]),
                "open_positions": 0,
                "open_trades": 0
            }
        except Exception:
            return {}

    async def get_open_positions(self) -> List[Dict]:
        """Fetch open contracts with re-auth."""
        await self.ensure_connection()
            
        req = {"portfolio": 1}
        try:
            await self.ws.send(json.dumps(req))
            resp = await self.ws.recv()
            data = json.loads(resp)
            
            if "error" in data:
                return []
                
            positions = []
            for contract in data.get("portfolio", {}).get("contracts", []):
                positions.append({
                    "instrument": contract["symbol"],
                    "units": 1, 
                    "unrealized_pl": float(contract["bid_price"]) - float(contract["buy_price"]),
                    "average_price": float(contract["buy_price"])
                })
            return positions
        except Exception:
            return []

    async def close(self):
        if self.ws:
            await self.ws.close()
