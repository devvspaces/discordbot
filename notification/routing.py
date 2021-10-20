from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    path('ws/webchat/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
]