import requests
import datetime

class DiscordNotifier:
    def __init__(self, config):
        self.webhook_url = config['discord']['webhook_url']

    def send_signal(self, symbol, signal_type, risk_data, session):
        """Sends a high-priority trade signal alert with session info."""
        color = 3066993 if "BUY" in signal_type else 15158332
        payload = {
            "embeds": [{
                "title": f"🚀 NEW SIGNAL: {symbol}",
                "description": f"**Action:** {signal_type}\n**Session:** {session}",
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

    def send_heartbeat(self, summary_list, session):
        """Sends a heartbeat with the current active trading session."""
        color = 9807270 
        description = "\n".join(summary_list)
        payload = {
            "embeds": [{
                "title": "💓 System Heartbeat",
                "description": f"**Active Session:** {session}\n\n**Market Scan:**\n{description}",
                "color": color,
                "footer": {"text": f"Status: Active | Time: {datetime.datetime.now().strftime('%H:%M')} UTC"}
            }]
        }
        requests.post(self.webhook_url, json=payload)
