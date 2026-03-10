import os
import yaml
import logging
from core.data_ingestion import DataManager
from risk_management.news_sentry import NewsSentry
from strategies.trend_following import TrendStrategy
from execution.discord_adapter import DiscordNotifier

def load_config():
    with open("config/settings.yaml", "r") as f:
        return yaml.safe_load(f)

def run_bot():
    # 1. Setup Logging & Config
    logging.basicConfig(level=logging.INFO)
    config = load_config()
    
    # 2. Initialize Modules
    data_manager = DataManager(config)
    news_sentry = NewsSentry(config)
    strategy = TrendStrategy(config)
    notifier = DiscordNotifier(config)

    # 3. Execution Flow
    for symbol in config['symbols']:
        logging.info(f"Analyzing {symbol}...")
        
        # Check News first (Phase 4 Logic)
        if news_sentry.is_market_volatile(symbol):
            logging.warning(f"Skipping {symbol} due to high-impact news.")
            continue
            
        # Get Data & Generate Signal (Phase 2 & 3)
        df = data_manager.get_latest_data(symbol)
        signal = strategy.check_signal(df)
        
        # If signal exists, send to Discord (Phase 5)
        if signal:
            notifier.send_signal(symbol, signal)

if __name__ == "__main__":
    run_bot()
