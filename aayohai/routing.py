from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
# from onlinecourse.token_auth import TokenAuthMiddlewareStack
from . import consumers
from .consumers import AdminNotifyConsumer

websocket_urlpatterns = [
    re_path(r'ws/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumerNew.as_asgi()),
    re_path(r'ws/admin/notifications/$', AdminNotifyConsumer.as_asgi()),

]
