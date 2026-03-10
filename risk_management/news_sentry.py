import requests
import logging
from datetime import datetime, timezone

class NewsSentry:
    def __init__(self, config):
        self.config = config
        self.url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        self.impact_levels = config.get('impact_levels', ['High'])

    def is_market_volatile(self, symbol):
        """Checks for high-impact news with defensive key handling."""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(self.url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return False
            
            events = response.json()
            now = datetime.now(timezone.utc)
            
            currencies = [symbol[:3], symbol[3:]]
            if "XAU" in symbol: currencies.append("USD")

            for event in events:
                # Defensive check: ensure keys exist before processing
                if all(k in event for k in ('impact', 'country', 'date', 'time')):
                    if event['impact'] in self.impact_levels and event['country'] in currencies:
                        try:
                            # Parse event time
                            event_dt_str = f"{event['date']} {event['time']}"
                            event_time = datetime.strptime(event_dt_str, "%m-%d-%Y %I:%M%p").replace(tzinfo=timezone.utc)
                            time_to_event = (event_time - now).total_seconds() / 60
                            
                            # Block if news is within 30 mins
                            if -15 < time_to_event < 30:
                                return True
                        except Exception:
                            continue
            return False
        except Exception as e:
            logging.error(f"News Sentry Failure: {e}")
            return False
