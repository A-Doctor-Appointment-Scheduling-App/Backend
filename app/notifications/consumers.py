import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Notification
import logging

logger = logging.getLogger('django')


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Log pour le débogage
        logger.info(f"Tentative de connexion WebSocket - URL parameters: {self.scope['url_route']['kwargs']}")
        
        self.user_type = self.scope['url_route']['kwargs']['user_type']
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        
        # Log pour le débogage
        logger.info(f"Consumer initialisé avec user_type={self.user_type}, user_id={self.user_id}")
        
        # Chaque utilisateur a son propre groupe pour recevoir ses notifications
        self.group_name = f"notifications_{self.user_id}_{self.user_type}"
        
        # Log pour le débogage
        logger.info(f"Groupe WebSocket: {self.group_name}")
        
        # Rejoindre le groupe
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info("Connexion WebSocket acceptée")
    
    async def disconnect(self, close_code):
        # Quitter le groupe
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    # Recevoir un message du WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # Si le client envoie une requête pour marquer une notification comme lue
        if data.get('type') == 'read_notification':
            notification_id = data.get('notification_id')
            success = await self.mark_notification_as_read(notification_id)
            # Confirmer au client
            await self.send(text_data=json.dumps({
                'type': 'notification_read',
                'notification_id': notification_id,
                'success': success
            }))
    
    # Gestionnaire pour envoyer une notification
    async def send_notification(self, event):
        # Envoyer le message au WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))
    
    @sync_to_async
    def mark_notification_as_read(self, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.is_read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False