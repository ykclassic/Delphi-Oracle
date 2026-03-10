import yfinance as yf
import pandas as pd
import logging
import time

class DataManager:
    def __init__(self, config):
        self.config = config
        self.timeframe = config.get('timeframe', '1h')
        
        # 2026 Best Practice: Use a custom User-Agent to prevent Yahoo blocks
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def get_latest_data(self, symbol):
        """Fetches OHLCV data with retries and custom headers."""
        # Convert Forex symbols to Yahoo format (EURUSD -> EURUSD=X)
        ticker_str = f"{symbol}=X" if "=" not in symbol and symbol != "XAUUSD" else symbol
        
        # Gold handling for Yahoo (XAUUSD=X or GC=F)
        if symbol == "XAUUSD":
            ticker_str = "GC=F" # Gold Futures is more reliable for intraday

        logging.info(f"Fetching data for {ticker_str}...")

        for attempt in range(3): # Try up to 3 times
            try:
                ticker = yf.Ticker(ticker_str)
                
                # We use history() instead of download() for better header control
                data = ticker.history(
                    period="1mo", 
                    interval=self.timeframe, 
                    raise_errors=True
                )
                
                if not data.empty:
                    # Reset index so 'Date' or 'Datetime' becomes a column
                    data = data.reset_index()
                    return data
                
                logging.warning(f"Attempt {attempt + 1}: Received empty data for {symbol}")
                
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed for {symbol}: {e}")
                time.sleep(2) # Wait 2 seconds before retry
        
        return None
