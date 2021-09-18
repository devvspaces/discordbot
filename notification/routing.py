from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    path('ws/webchat/<room_name>/', consumers.ChatConsumer.as_asgi()),
    # re_path(r'ws/webchat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]