from django.urls import path
from . import consumers  # Импортируем обработчик WebSocket

websocket_urlpatterns = [
    path('ws/chat/<int:order_id>/', consumers.ChatConsumer.as_asgi()),
]