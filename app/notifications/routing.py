from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/notifications/(?P<user_id>\d+)/(?P<user_type>\w+)/$', consumers.NotificationConsumer.as_asgi()),    
]