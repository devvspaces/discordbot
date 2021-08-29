# chat/consumers.py
import json

import logging

# Create the logger and set the logging level
logger = logging.getLogger('basic')
err_logger = logging.getLogger('basic.error')


from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from account.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, *args, **kwargs):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from room group
    async def channel_message(self, event):
        message = event['message']
        mtype = event['mtype']
        count = event['count']

        logger.debug('Consumer sent message to listeners')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'type': mtype,
            'count': count,
        }))