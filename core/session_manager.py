import datetime

class SessionManager:
    def get_current_session(self):
        """Returns the active Forex session(s) based on UTC time."""
        now = datetime.datetime.now(datetime.timezone.utc).hour
        
        sessions = []
        # Standard 2026 Forex Session Hours (UTC)
        if 0 <= now < 9: sessions.append("Tokyo 🇯🇵")
        if 8 <= now < 17: sessions.append("London 🇬🇧")
        if 13 <= now < 22: sessions.append("New York 🇺🇸")
        if 21 <= now <= 23 or 0 <= now < 6: sessions.append("Sydney 🇦🇺")
        
        if not sessions:
            return "Market Closed"
        
        return " & ".join(sessions)
