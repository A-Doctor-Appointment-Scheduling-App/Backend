from firebase_admin import messaging
from .models import FCMDevice

def send_push_notification(user_id, user_type, title, body, data=None):
    """
    Envoie une notification push via FCM
    """
    # Récupérer tous les tokens pour cet utilisateur
    devices = FCMDevice.objects.filter(user_id=user_id, user_type=user_type, active=True)
    
    if not devices.exists():
        return False  # Pas d'appareil enregistré pour cet utilisateur
    
    # Préparation des données
    message_data = data or {}
    
    # Pour chaque appareil enregistré, envoyer la notification
    for device in devices:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=message_data,
            token=device.registration_id,
        )
        
        try:
            response = messaging.send(message)
            print(f"Successfully sent message: {response}")
        except Exception as e:
            print(f"Error sending message to {device.registration_id}: {e}")
            # Désactiver le token s'il n'est plus valide
            if "invalid-registration-token" in str(e).lower():
                device.active = False
                device.save()
    
    return True