import pandas as pd
import logging
from core.data_ingestion import DataManager

class SignalMonitor:
    def __init__(self, config):
        self.config = config
        self.log_path = "logs/trade_log.csv"
        self.data_manager = DataManager(config)

    def check_outcomes(self):
        """Analyzes active signals against current live data strictly sequentially."""
        try:
            df_logs = pd.read_csv(self.log_path)
        except FileNotFoundError:
            return []

        if 'Outcome' not in df_logs.columns:
            df_logs['Outcome'] = 'Pending'
            
        # Clean up missing outcome values
        df_logs['Outcome'] = df_logs['Outcome'].fillna('Pending')

        updates = []
        for idx, row in df_logs.iterrows():
            # Filter out non-pending trades, uninitialized polling rows, and NaN signals
            if (row['Outcome'] != 'Pending' or 
                pd.isna(row['Signal']) or 
                str(row['Signal']).strip() == 'None' or 
                row['Entry'] == 0.0):
                continue

            symbol = row['Symbol']
            trade_time = pd.to_datetime(row['Timestamp'])
            
            data = self.data_manager.get_latest_data(symbol)
            if data is None or data.empty:
                continue

            # Standardize index to datetime for accurate chronological slicing
            if not pd.api.types.is_datetime64_any_dtype(data.index):
                data.index = pd.to_datetime(data.index)

            # Restrict evaluation strictly to price action AFTER the trade execution
            future_data = data[data.index > trade_time]
            if future_data.empty:
                continue

            outcome = "Pending"
            trigger_price = future_data['Close'].iloc[-1]
            
            # Evaluate sequentially to avoid intra-bar look-ahead bias and dual-trigger collision
            for _, candle in future_data.iterrows():
                high = candle['High']
                low = candle['Low']
                
                if "BUY" in str(row['Signal']):
                    # In a conservative backtest/forward-test, Stop Loss is prioritized if both are hit
                    if low <= row['SL']: 
                        outcome = "❌ STOP LOSS"
                        trigger_price = row['SL']
                        break
                    elif high >= row['TP']: 
                        outcome = "✅ TAKE PROFIT"
                        trigger_price = row['TP']
                        break
                elif "SELL" in str(row['Signal']):
                    if high >= row['SL']: 
                        outcome = "❌ STOP LOSS"
                        trigger_price = row['SL']
                        break
                    elif low <= row['TP']: 
                        outcome = "✅ TAKE PROFIT"
                        trigger_price = row['TP']
                        break

            if outcome != "Pending":
                df_logs.at[idx, 'Outcome'] = outcome
                updates.append(f"**{symbol}**: {outcome} at price {trigger_price:.5f}")

        df_logs.to_csv(self.log_path, index=False)
        return updates
