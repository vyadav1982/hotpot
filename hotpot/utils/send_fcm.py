# from firebase_config import messaging
# from .firebase_config import messaging
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebase_config import messaging


def send_notification_by_token(device_token, title, body,date=None, doc_id=None, text=None):
	data_payload = {
        "date": str(date) or "",
        "id": str(doc_id) if doc_id else "",
        "text": text or ""
    }
	message = messaging.Message(
		notification=messaging.Notification(
			title=title,
			body=body,
		),
		token=device_token,
		data=data_payload
	)
	response = messaging.send(message)
	print("Successfully send message:", response)
