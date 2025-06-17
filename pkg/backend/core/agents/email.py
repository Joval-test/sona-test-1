from core.leads import send_email_real
import os
import json
import config

class EmailAgent:
    def __init__(self, email_client=None):
        self.email_client = email_client

    def send_meeting_invite(self, to_email: str, meeting_link: str, details: dict) -> bool:
        """
        Send a meeting invite email.
        Args:
            to_email (str): Recipient email.
            meeting_link (str): Meeting link URL.
            details (dict): Additional meeting details.
        Returns:
            bool: Success status.
        """
        sender_email = config.EMAIL_SENDER
        sender_password = config.EMAIL_PASSWORD
        subject = details.get('subject', 'Meeting Scheduled')
        message = f"You have a meeting scheduled.\nMeeting Link: {meeting_link}\nDetails: {details.get('body', '')}"
        return send_email_real(sender_email, sender_password, to_email, subject, message) 