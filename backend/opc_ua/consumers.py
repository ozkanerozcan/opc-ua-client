from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json

class OPCConsumer(WebsocketConsumer):
    def connect(self):
        # Accept WebSocket connection
        self.accept()

        # Add client to "opcua_updates" group
        async_to_sync(self.channel_layer.group_add)(
            "opcua_updates",
            self.channel_name
        )

    def disconnect(self, close_code):
        # Remove client from "opcua_updates" group
        async_to_sync(self.channel_layer.group_discard)(
            "opcua_updates",
            self.channel_name
        )

    def send_update(self, event):
        """Send OPC UA updates to frontend"""
        data = event['data']
        self.send(text_data=data)
