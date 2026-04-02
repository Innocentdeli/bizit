import yfinance as yf
import threading
import time
from typing import Callable

class MarketCollector:
    """
    Level 11: Reality Feed.
    Injects real-world financial data (BTC, S&P 500) into the BIZIT Sensory Stream.
    """
    def __init__(self, symbols=["BTC-USD", "^GSPC"], callback: Callable = None):
        self.symbols = symbols
        self.callback = callback
        self.running = True
        self.last_prices = {s: 0.0 for s in symbols}

    def start(self):
        threading.Thread(target=self._pull_data, daemon=True).start()

    def _pull_data(self):
        print(f"[REALITY] Injecting Market Stream: {self.symbols}")
        while self.running:
            try:
                for symbol in self.symbols:
                    ticker = yf.Ticker(symbol)
                    # Get fast info
                    price = ticker.fast_info['last_price']
                    
                    if price != self.last_prices[symbol]:
                        print(f"[REALITY] {symbol} Update: ${price:,.2f}")
                        if self.callback:
                            self.callback({
                                "event_type": "MARKET_TICK",
                                "source": "yfinance",
                                "payload": {
                                    "symbol": symbol,
                                    "price": price,
                                    "delta": price - self.last_prices[symbol]
                                },
                                "timestamp": time.time(),
                                "tags": ["reality_feed"]
                            })
                        self.last_prices[symbol] = price
                        
                time.sleep(10) # Accelerated for verification
            except Exception as e:
                print(f"[REALITY] Market Feed Error: {e}")
                time.sleep(10)
