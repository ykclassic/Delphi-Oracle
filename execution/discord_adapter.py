import requests
import datetime

class DiscordNotifier:
    def __init__(self, config):
        self.webhook_url = config['discord']['webhook_url']

    def send_signal(self, symbol, signal_type, risk_data):
        """Sends a high-priority trade signal alert."""
        color = 3066993 if "BUY" in signal_type else 15158332
        payload = {
            "embeds": [{
                "title": f"🚀 NEW SIGNAL: {symbol}",
                "description": f"**Action:** {signal_type}",
                "color": color,
                "fields": [
                    {"name": "Entry", "value": f"{risk_data['entry']}", "inline": True},
                    {"name": "Stop Loss", "value": f"{risk_data['sl']}", "inline": True},
                    {"name": "Take Profit", "value": f"{risk_data['tp']}", "inline": True}
                ],
                "footer": {"text": f"Delphi Oracle v1.0 | {datetime.datetime.now().strftime('%H:%M:%S')} UTC"}
            }]
        }
        requests.post(self.webhook_url, json=payload)

    def send_heartbeat(self, summary_list):
        """Sends a low-priority status update to confirm the bot is active."""
        # Grey color for heartbeat
        color = 9807270 
        
        description = "\n".join(summary_list)
        payload = {
            "embeds": [{
                "title": "💓 System Heartbeat",
                "description": f"**Market Scan Complete:**\n{description}",
                "color": color,
                "footer": {"text": f"Status: Active | Next scan in 1 hour"}
            }]
        }
        requests.post(self.webhook_url, json=payload)
