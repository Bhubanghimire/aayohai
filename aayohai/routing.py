from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
# from onlinecourse.token_auth import TokenAuthMiddlewareStack
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
