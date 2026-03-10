import pandas as pd
import logging
from core.data_ingestion import DataManager

class SignalMonitor:
    def __init__(self, config):
        self.config = config
        self.log_path = "logs/trade_log.csv"
        self.data_manager = DataManager(config)

    def check_outcomes(self):
        """Analyzes active signals against current live data."""
        try:
            df_logs = pd.read_csv(self.log_path)
        except FileNotFoundError:
            return []

        if 'Outcome' not in df_logs.columns:
            df_logs['Outcome'] = 'Pending'

        updates = []
        for idx, row in df_logs.iterrows():
            if row['Outcome'] != 'Pending' or row['Signal'] == 'None':
                continue

            symbol = row['Symbol']
            # Fetch high-fidelity data for exit check
            data = self.data_manager.get_latest_data(symbol)
            if data is None: continue

            price = data['Close'].iloc[-1]
            high = data['High'].max()
            low = data['Low'].min()
            
            outcome = "Pending"
            if "BUY" in row['Signal']:
                if high >= row['TP']: outcome = "✅ TAKE PROFIT"
                elif low <= row['SL']: outcome = "❌ STOP LOSS"
            elif "SELL" in row['Signal']:
                if low <= row['TP']: outcome = "✅ TAKE PROFIT"
                elif high >= row['SL']: outcome = "❌ STOP LOSS"

            if outcome != "Pending":
                df_logs.at[idx, 'Outcome'] = outcome
                updates.append(f"**{symbol}**: {outcome} at price {price:.5f}")

        df_logs.to_csv(self.log_path, index=False)
        return updates
