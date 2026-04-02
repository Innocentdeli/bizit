"""
Level 52: The Father's Alpha - Tri-Confluence Engine
Complete rebuild implementing exact multi-timeframe methodology.
"""

import math
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class TriConfluenceEngine:
    """
    The Father's Alpha Strategy - Surgical Precision Edition
    
    Tri-Confluence Components:
    1. Psychological Levels (00/50 round numbers)
    2. Weekly High/Low (first 2 x 4H candles, recalculated Monday)
    3. Parent Timeframe S/R (gives entry/exit points)
    
    Entry Logic:
    - Step 1: 4H breaks Weekly H/L
    - Step 2: Child TF breaks Psychological Level
    - Step 3: Child TF breaks Parent S/R
    → ENTER with 30-pip SL
    
    Exit Logic:
    - Touch next Parent S/R in trade direction (not the broken one)
    """
    
    def __init__(self, symbol: str = "GBPUSD"):
        self.symbol = symbol
        
        # Level 53: Universal Asset Eye
        if "JPY" in symbol:
            self.pip_size = 0.01 
        elif "XAU" in symbol: # Gold
            self.pip_size = 0.01
        elif "BTC" in symbol: # Bitcoin
            self.pip_size = 1.0
        else:
            self.pip_size = 0.0001
        
        # S/R Cache for all timeframes
        self.sr_cache = {
            "MONTHLY": {"supports": [], "resistances": []},
            "WEEKLY": {"supports": [], "resistances": []},
            "DAILY": {"supports": [], "resistances": []},
            "4H": {"supports": [], "resistances": []}
        }
        
        # Weekly H/L state
        self.weekly_hl = {
            "high": None,
            "low": None,
            "calculated_at": None,
            "is_valid": False
        }
        
        # Psychological levels cache
        self.psychological_levels = []
    
    def get_pip_dist(self, p1: float, p2: float) -> float:
        """Calculate pip distance between two prices."""
        return abs(p1 - p2) / self.pip_size
    
    # ==================== 1. MULTI-TIMEFRAME S/R DETECTION ====================
    
    def detect_sr_levels(self, candles: List[Dict], k: int = 3) -> Dict[str, List[float]]:
        """
        Detect Support/Resistance using swing pivot method.
        
        Args:
            candles: List of OHLC candles
            k: Lookback period (default 3)
        
        Returns:
            {"supports": [1.3200, 1.3150], "resistances": [1.3550, 1.3600]}
        """
        if len(candles) < (2 * k + 1):
            return {"supports": [], "resistances": []}
        
        highs = [c['high'] for c in candles]
        lows = [c['low'] for c in candles]
        
        resistances = []
        supports = []
        
        for i in range(k, len(candles) - k):
            # Resistance: High is max in window
            window_h = highs[i-k : i+k+1]
            if highs[i] == max(window_h):
                resistances.append(highs[i])
            
            # Support: Low is min in window
            window_l = lows[i-k : i+k+1]
            if lows[i] == min(window_l):
                supports.append(lows[i])
        
        # Remove duplicates and sort
        supports = sorted(list(set(supports)))
        resistances = sorted(list(set(resistances)))
        
        return {"supports": supports, "resistances": resistances}
    
    def update_sr_for_timeframe(self, candles: List[Dict], timeframe: str, k: int = 3):
        """Update S/R cache for a specific timeframe."""
        sr = self.detect_sr_levels(candles, k)
        self.sr_cache[timeframe] = sr
    
    def invalidate_broken_sr(self, timeframe: str, broken_price: float, direction: str):
        """
        Remove S/R level once price closes beyond it.
        
        Args:
            timeframe: "MONTHLY", "WEEKLY", "DAILY", "4H"
            broken_price: Price that was broken
            direction: "BULLISH" or "BEARISH"
        """
        sr = self.sr_cache[timeframe]
        
        if direction == "BULLISH":
            # Remove broken resistance
            sr["resistances"] = [r for r in sr["resistances"] if r > broken_price + (5 * self.pip_size)]
        else:
            # Remove broken support
            sr["supports"] = [s for s in sr["supports"] if s < broken_price - (5 * self.pip_size)]
    
    # ==================== 2. PSYCHOLOGICAL LEVEL GENERATOR ====================
    
    def generate_psychological_levels(self, current_price: float, pip_interval: int = 50, range_pips: int = 200):
        """
        Generate psychological levels (00/50 round numbers).
        
        Args:
            current_price: Current market price
            pip_interval: 50 for major levels
            range_pips: Generate levels within ±range_pips
        
        Returns:
            List of psychological levels
        """
        step = pip_interval * self.pip_size
        
        # Find nearest psych level
        base = round(current_price / step) * step
        
        # Generate levels within range
        levels = []
        range_price = range_pips * self.pip_size
        
        level = base - range_price
        while level <= base + range_price:
            levels.append(round(level, 5))
            level += step
        
        self.psychological_levels = levels
        return levels
    
    def get_nearest_psych_level(self, price: float) -> float:
        """Get closest psychological level to price."""
        if not self.psychological_levels:
            self.generate_psychological_levels(price)
        
        return min(self.psychological_levels, key=lambda x: abs(x - price))
    
    # ==================== 3. WEEKLY HIGH/LOW CALCULATOR ====================
    
    def calculate_weekly_hl(self, candles_4h: List[Dict], current_datetime: datetime = None):
        """
        Calculate Weekly H/L from first 2 x 4H candles of the week.
        
        Args:
            candles_4h: 4H candle data (must include 'time' field as timestamp)
            current_datetime: Current datetime (defaults to now)
        
        Updates:
            self.weekly_hl with high/low values
        """
        if current_datetime is None:
            current_datetime = datetime.now()
        
        # Find Monday 00:00 of current week
        days_since_monday = current_datetime.weekday()
        monday = current_datetime - timedelta(days=days_since_monday)
        monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check if we need to recalculate (new week)
        if self.weekly_hl["calculated_at"]:
            last_calc = datetime.fromtimestamp(self.weekly_hl["calculated_at"])
            if last_calc >= monday:
                # Already calculated for this week
                return self.weekly_hl
        
        # Find first 2 x 4H candles of the week
        monday_ts = monday.timestamp()
        first_8h_candles = [c for c in candles_4h if c.get('time', 0) >= monday_ts and c.get('time', 0) < monday_ts + (8 * 3600)]
        
        if len(first_8h_candles) < 2:
            self.weekly_hl["is_valid"] = False
            return self.weekly_hl
        
        # Get highest high and lowest low from first 2 candles
        highs = [c['high'] for c in first_8h_candles[:2]]
        lows = [c['low'] for c in first_8h_candles[:2]]
        
        self.weekly_hl = {
            "high": max(highs),
            "low": min(lows),
            "calculated_at": current_datetime.timestamp(),
            "is_valid": True
        }
        
        return self.weekly_hl
    
    # ==================== 4. TRI-CONFLUENCE SCANNER ====================
    
    def check_tri_confluence(
        self,
        trading_timeframe: str,  # "4H", "DAILY", "WEEKLY", "MONTHLY"
        candles_4h: List[Dict],
        candles_child: List[Dict],  # 1H for 4H trading, 4H for Daily, etc.
        current_price: float,
        prev_price: float
    ) -> Optional[Dict]:
        """
        Check if all 3 confluence conditions are met for entry.
        
        Returns signal dict if all conditions pass, None otherwise.
        """
        # Ensure we have weekly H/L
        if not self.weekly_hl["is_valid"]:
            return None
        
        # Ensure we have psychological levels
        if not self.psychological_levels:
            self.generate_psychological_levels(current_price)
        
        # Get parent S/R based on trading timeframe
        parent_tf_map = {
            "4H": "4H",
            "DAILY": "DAILY",
            "WEEKLY": "WEEKLY",
            "MONTHLY": "MONTHLY"
        }
        parent_tf = parent_tf_map.get(trading_timeframe)
        if not parent_tf:
            return None
        
        parent_sr = self.sr_cache[parent_tf]
        
        # Step 1: Check if 4H broke Weekly H/L
        step1_bullish = self._check_4h_breaks_weekly_high(candles_4h)
        step1_bearish = self._check_4h_breaks_weekly_low(candles_4h)
        
        if not (step1_bullish or step1_bearish):
            return None
        
        # Step 2 & 3: Check child TF breaks psych + parent S/R
        if step1_bullish:
            signal = self._check_bullish_entry(
                current_price, prev_price,
                parent_sr["resistances"]
            )
            if signal:
                signal["direction"] = "LONG"
                signal["entry_price"] = current_price
                signal["sl_price"] = current_price - (30 * self.pip_size)
                signal["exit_target"] = self._find_exit_target(current_price, "LONG", parent_sr["resistances"])
                return signal
        
        if step1_bearish:
            signal = self._check_bearish_entry(
                current_price, prev_price,
                parent_sr["supports"]
            )
            if signal:
                signal["direction"] = "SHORT"
                signal["entry_price"] = current_price
                signal["sl_price"] = current_price + (30 * self.pip_size)
                signal["exit_target"] = self._find_exit_target(current_price, "SHORT", parent_sr["supports"])
                return signal
        
        return None
    
    def _check_4h_breaks_weekly_high(self, candles_4h: List[Dict]) -> bool:
        """Check if latest 4H candle closed above Weekly High."""
        if not candles_4h or not self.weekly_hl["is_valid"]:
            return False
        
        latest_close = candles_4h[-1]['close']
        return latest_close > self.weekly_hl["high"]
    
    def _check_4h_breaks_weekly_low(self, candles_4h: List[Dict]) -> bool:
        """Check if latest 4H candle closed below Weekly Low."""
        if not candles_4h or not self.weekly_hl["is_valid"]:
            return False
        
        latest_close = candles_4h[-1]['close']
        return latest_close < self.weekly_hl["low"]
    
    def _check_bullish_entry(self, current_price: float, prev_price: float, resistances: List[float]) -> Optional[Dict]:
        """Check Step 2 & 3 for bullish entry."""
        # Step 2: Check if price broke psych level
        nearest_psych = self.get_nearest_psych_level(current_price)
        if not (prev_price < nearest_psych and current_price > nearest_psych):
            return None
        
        # Step 3: Check if price broke parent resistance
        for resistance in resistances:
            if prev_price < resistance and current_price > resistance:
                return {
                    "step1": True,
                    "step2_psych_break": True,
                    "step3_sr_break": True,
                    "broken_sr": resistance
                }
        
        return None
    
    def _check_bearish_entry(self, current_price: float, prev_price: float, supports: List[float]) -> Optional[Dict]:
        """Check Step 2 & 3 for bearish entry."""
        # Step 2: Check if price broke psych level
        nearest_psych = self.get_nearest_psych_level(current_price)
        if not (prev_price > nearest_psych and current_price < nearest_psych):
            return None
        
        # Step 3: Check if price broke parent support
        for support in supports:
            if prev_price > support and current_price < support:
                return {
                    "step1": True,
                    "step2_psych_break": True,
                    "step3_sr_break": True,
                    "broken_sr": support
                }
        
        return None
    
    # ==================== 5. EXIT TARGET FINDER ====================
    
    def _find_exit_target(self, current_price: float, direction: str, sr_levels: List[float]) -> Optional[float]:
        """
        Find next parent S/R in trade direction (not the broken one).
        
        Args:
            current_price: Current price
            direction: "LONG" or "SHORT"
            sr_levels: Parent S/R levels
        
        Returns:
            Next S/R price for exit
        """
        if not sr_levels:
            return None
        
        if direction == "LONG":
            # Find next resistance above current price
            targets = [r for r in sr_levels if r > current_price + (10 * self.pip_size)]
            return min(targets) if targets else None
        else:
            # Find next support below current price
            targets = [s for s in sr_levels if s < current_price - (10 * self.pip_size)]
            return max(targets) if targets else None
    
    def check_exit_touch(self, current_price: float, exit_target: float, direction: str) -> bool:
        """Check if price has touched exit target."""
        if not exit_target:
            return False
        
        tolerance = 5 * self.pip_size
        
        if direction == "LONG":
            return current_price >= (exit_target - tolerance)
        else:
            return current_price <= (exit_target + tolerance)
