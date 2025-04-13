import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Message, Chat

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'chat_{self.order_id}'

        # Присоединяемся к группе чата
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Покидаем группу чата
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Обработка входящих сообщений
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']

        # Сохраняем сообщение в базе данных
        chat = await sync_to_async(Chat.objects.get)(order_id=self.order_id)
        sender = await sync_to_async(User.objects.get)(id=sender_id)
        new_message = await sync_to_async(Message.objects.create)(
            chat=chat,
            sender=sender,
            text=message
        )

        # Отправляем сообщение всем участникам группы
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'timestamp': str(new_message.created_at)
            }
        )

    # Отправка сообщения клиентам
    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']
        timestamp = event['timestamp']

        # Отправляем сообщение через WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'timestamp': timestamp
        }))