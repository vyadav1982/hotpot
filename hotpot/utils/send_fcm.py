from firebase_config import messaging

def send_notification_by_token(device_token, title, body):
    message = messaging.Message(
        notification = messaging.Notification(
            title=title,
            body=body,
        ),
        token = device_token,
    )
    response = messaging.send(message)
    print("Successfully send message:", response)