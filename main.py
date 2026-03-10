import os
import yaml
import logging
from core.data_ingestion import DataManager
from core.regime_detector import RegimeDetector
from risk_management.news_sentry import NewsSentry
from risk_management.position_sizer import PositionSizer
from strategies.trend_following import TrendStrategy
from execution.discord_adapter import DiscordNotifier

def load_config():
    with open("config/settings.yaml", "r") as f:
        config = yaml.safe_load(f)
    webhook_env = os.getenv("DISCORD_WEBHOOK_URL")
    if webhook_env:
        config['discord']['webhook_url'] = webhook_env
    return config

def run_bot():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    config = load_config()
    
    # Initialize Modules
    data_manager = DataManager(config)
    regime_detector = RegimeDetector()
    news_sentry = NewsSentry(config)
    strategy = TrendStrategy(config)
    position_sizer = PositionSizer(config)
    notifier = DiscordNotifier(config)

    summary_results = []

    for symbol in config['symbols']:
        # 1. News Check
        if news_sentry.is_market_volatile(symbol):
            summary_results.append(f"⚪ {symbol}: Paused (High Impact News)")
            continue
            
        # 2. Data Check
        df = data_manager.get_latest_data(symbol)
        if df is None or len(df) < 50:
            summary_results.append(f"🔴 {symbol}: Data Error")
            continue
            
        # 3. Intelligence & Signal
        regime = regime_detector.classify(df)
        signal_type = strategy.generate_signal(df, regime)
        
        # Mapping emoji to regime
        regime_emoji = {0: "🟦", 1: "🟩", 2: "🟧"} # Range, Trend, Chaos
        
        if signal_type:
            risk_data = position_sizer.calculate(df, symbol, signal_type)
            notifier.send_signal(symbol, signal_type, risk_data)
            summary_results.append(f"🔥 {symbol}: SIGNAL SENT ({signal_type})")
        else:
            summary_results.append(f"{regime_emoji.get(regime, '⚪')} {symbol}: Scanning (No Setup)")

    # 4. Final Heartbeat
    notifier.send_heartbeat(summary_results)
    logging.info("Heartbeat sent. Scan cycle complete.")

if __name__ == "__main__":
    run_bot()
