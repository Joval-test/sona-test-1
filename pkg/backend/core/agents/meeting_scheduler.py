from core.agents.google_auth import GoogleAuthManager
from datetime import datetime, timedelta

class MeetingSchedulerAgent:
    def __init__(self, meeting_client=None):
        self.meeting_client = meeting_client
        self.google_auth = GoogleAuthManager()

    def create_meeting(self, time_slot: str, participants: list) -> str:
        """
        Create a Google Calendar event with a Meet link for the given time slot and participants.
        Returns the meeting link URL.
        """
        creds = self.google_auth.get_credentials()
        if not creds:
            return ""
        from googleapiclient.discovery import build
        service = build('calendar', 'v3', credentials=creds)
        start = time_slot
        end = (datetime.fromisoformat(time_slot.replace('Z', '')) + timedelta(hours=1)).isoformat() + 'Z'
        event = {
            'summary': 'Scheduled Meeting',
            'start': {'dateTime': start, 'timeZone': 'UTC'},
            'end': {'dateTime': end, 'timeZone': 'UTC'},
            'attendees': [{'email': email} for email in participants],
            'conferenceData': {
                'createRequest': {
                    'requestId': 'meet-' + start.replace(':', '').replace('-', '').replace('T', '')
                }
            }
        }
        try:
            created_event = service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1
            ).execute()
            meet_link = created_event.get('hangoutLink', '')
            return meet_link
        except Exception:
            return "" 