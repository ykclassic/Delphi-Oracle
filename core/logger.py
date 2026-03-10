import pandas as pd
import datetime
import os

class PerformanceLogger:
    def __init__(self, file_path="logs/trade_log.csv"):
        self.file_path = file_path
        # Ensure the logs directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        # Initialize file with headers if it doesn't exist
        if not os.path.exists(self.file_path):
            df = pd.DataFrame(columns=[
                "Timestamp", "Symbol", "Regime", "Signal", 
                "Entry", "SL", "TP", "Outcome"
            ])
            df.to_csv(self.file_path, index=False)

    def log_scan(self, symbol, regime, signal=None, risk_data=None):
        """Logs every scan attempt to the CSV."""
        log_entry = {
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Symbol": symbol,
            "Regime": regime,
            "Signal": signal if signal else "None",
            "Entry": risk_data['entry'] if risk_data else 0.0,
            "SL": risk_data['sl'] if risk_data else 0.0,
            "TP": risk_data['tp'] if risk_data else 0.0,
            "Outcome": "Pending" if signal else "N/A"
        }
        
        df = pd.DataFrame([log_entry])
        df.to_csv(self.file_path, mode='a', header=False, index=False)
