from pyfcm import FCMNotification
from django.conf import settings

push_service = FCMNotification(api_key=settings.FCM_SERVER_KEY)

def send_fcm_notification(token, title, message):
    result = push_service.notify_single_device(
        registration_id=token,
        message_title=title,
        message_body=message
    )
    return result