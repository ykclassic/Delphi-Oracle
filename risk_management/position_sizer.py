import logging

class PositionSizer:
    def __init__(self, config):
        self.config = config
        self.risk_pct = config.get('risk_per_trade_percent', 1.0)
        # Max allowable spread as a percentage of the total target
        self.max_spread_cost_pct = 0.15 # 15% max

    def calculate(self, df, symbol, signal_type):
        """Calculates TP/SL and checks if spread makes the trade low-quality."""
        last_price = df['Close'].iloc[-1]
        atr = df['ATR'].iloc[-1]
        
        # 1. Dynamic SL/TP based on Volatility (ATR)
        if "BUY" in signal_type:
            sl = last_price - (atr * self.config.get('default_stop_loss_atr', 1.5))
            tp = last_price + (atr * self.config.get('default_take_profit_ratio', 2.0))
        else: # SELL
            sl = last_price + (atr * self.config.get('default_stop_loss_atr', 1.5))
            tp = last_price - (atr * self.config.get('default_take_profit_ratio', 2.0))

        # 2. Quality Filter: The Spread Guard
        # In a real broker API, we'd fetch 'ask' - 'bid'. 
        # Since we use Yahoo (delayed), we estimate spread based on symbol type.
        estimated_spread = self._estimate_spread(symbol)
        potential_profit = abs(tp - last_price)
        
        if (estimated_spread / potential_profit) > self.max_spread_cost_pct:
            logging.warning(f"QUALITY ALERT: Spread on {symbol} is too high for this target. Aborting.")
            return None # This tells main.py to skip the signal

        return {
            "entry": round(last_price, 5),
            "sl": round(sl, 5),
            "tp": round(tp, 5)
        }

    def _estimate_spread(self, symbol):
        """Estimates typical 2026 spreads if live data isn't available."""
        # Standard pips converted to price points
        spreads = {
            "EURUSD": 0.00012, "GBPUSD": 0.00018, 
            "USDJPY": 0.012, "EURJPY": 0.018, "GBPJPY": 0.025,
            "XAUUSD": 0.35
        }
        return spreads.get(symbol, 0.0002) # Default fallback
