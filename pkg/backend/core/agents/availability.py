from core.agents.google_auth import GoogleAuthManager
from datetime import datetime, timedelta

class AvailabilityAgent:
    def __init__(self, calendar_client=None):
        self.calendar_client = calendar_client
        self.google_auth = GoogleAuthManager()

    def check_availability(self, person1_email: str, person2_email: str) -> list:
        """
        Check mutual available time slots for two people using Google Calendar API.
        Returns a list of ISO8601 time slots.
        """
        creds = self.google_auth.get_credentials()
        if not creds:
            return []
        from googleapiclient.discovery import build
        service = build('calendar', 'v3', credentials=creds)
        now = datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=7)).isoformat() + 'Z'
        body = {
            "timeMin": time_min,
            "timeMax": time_max,
            "items": [
                {"id": person1_email},
                {"id": person2_email}
            ]
        }
        try:
            eventsResult = service.freebusy().query(body=body).execute()
            busy1 = eventsResult['calendars'][person1_email]['busy']
            busy2 = eventsResult['calendars'][person2_email]['busy']
            # Find a 1-hour slot where both are free (naive implementation)
            slot = self.find_mutual_free_slot(busy1, busy2, now, now + timedelta(days=7))
            return [slot] if slot else []
        except Exception:
            return []

    def find_mutual_free_slot(self, busy1, busy2, start, end):
        # For demo: just return the next hour if both are free
        slot_start = start.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        slot_end = slot_start + timedelta(hours=1)
        slot_str = slot_start.isoformat() + 'Z'
        # Check if slot overlaps with any busy period
        for b in busy1 + busy2:
            b_start = datetime.fromisoformat(b['start'].replace('Z', ''))
            b_end = datetime.fromisoformat(b['end'].replace('Z', ''))
            if b_start < slot_end and b_end > slot_start:
                return None
        return slot_str 