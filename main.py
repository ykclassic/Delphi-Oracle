import os
import yaml
import logging
import pandas as pd
from core.data_ingestion import DataManager
from core.regime_detector import RegimeDetector
from risk_management.news_sentry import NewsSentry
from risk_management.position_sizer import PositionSizer
from strategies.trend_following import TrendStrategy
from execution.discord_adapter import DiscordNotifier

def load_config():
    """Loads settings and resolves secrets from environment variables."""
    with open("config/settings.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    # Resolve Discord Webhook from GitHub Secrets
    webhook_env = os.getenv("DISCORD_WEBHOOK_URL")
    if webhook_env:
        config['discord']['webhook_url'] = webhook_env
    
    return config

def run_bot():
    # 1. Initialization & Logging
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Initializing Delphi Oracle Forex Bot...")
    
    config = load_config()
    if not config['discord'].get('webhook_url'):
        logging.error("CRITICAL: DISCORD_WEBHOOK_URL is missing. Check GitHub Secrets.")
        return

    # 2. Module Instantiation
    data_manager = DataManager(config)
    regime_detector = RegimeDetector()
    news_sentry = NewsSentry(config)
    strategy = TrendStrategy(config)
    position_sizer = PositionSizer(config)
    notifier = DiscordNotifier(config)

    # 3. Main Loop: Iterate through Currency Pairs
    for symbol in config['symbols']:
        logging.info(f"--- Process Start: {symbol} ---")
        
        # A. High-Impact News Filter
        if news_sentry.is_market_volatile(symbol):
            logging.warning(f"Strategy Paused: High-impact news detected for {symbol}. Standing down.")
            continue
            
        # B. Data Acquisition
        df = data_manager.get_latest_data(symbol)
        if df is None or len(df) < 100:
            logging.warning(f"Data Error: Insufficient history for {symbol}. Skipping.")
            continue
            
        # C. Market Intelligence (Regime Detection)
        # 0 = Range, 1 = Trend, 2 = Chaos
        regime = regime_detector.classify(df)
        regime_names = {0: "Range (Mean Reversion)", 1: "Trending (Momentum)", 2: "Chaos (High Volatility)"}
        logging.info(f"Market Context for {symbol}: {regime_names.get(regime)}")

        # D. Signal Generation (Logic specific to current Regime)
        signal_type = strategy.generate_signal(df, regime)
        
        # E. Execution & Alerting
        if signal_type:
            logging.info(f"SIGNAL FOUND: {signal_type} for {symbol}!")
            
            # Calculate Risk: SL, TP, and Lot Size
            risk_data = position_sizer.calculate(df, symbol, signal_type)
            
            # Send to Discord
            success = notifier.send_signal(symbol, signal_type, risk_data)
            if success:
                logging.info(f"Alert sent successfully to Discord for {symbol}.")
            else:
                logging.error(f"Failed to send Discord alert for {symbol}.")
        else:
            logging.info(f"Analysis complete: No valid setup found for {symbol} at this time.")

    logging.info("All pairs processed. Bot entering standby.")

if __name__ == "__main__":
    run_bot()
