import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger('django')

class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Log explicite
        print("TEST CONSUMER: Tentative de connexion reçue!")
        logger.info("TEST CONSUMER: Tentative de connexion reçue!")
        
        await self.accept()
        
        # Log après acceptation
        print("TEST CONSUMER: Connexion acceptée!")
        logger.info("TEST CONSUMER: Connexion acceptée!")
        
        # Envoyer un message test
        await self.send(text_data=json.dumps({
            'type': 'test_connection',
            'message': 'WebSocket test successful'
        }))
    
    async def disconnect(self, close_code):
        print(f"TEST CONSUMER: Déconnexion avec code {close_code}")
        logger.info(f"TEST CONSUMER: Déconnexion avec code {close_code}")