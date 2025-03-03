"""
ASGI config for aayohai project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aayohai.settings")

# Set up Django
django.setup()

from aayohai.routing import websocket_urlpatterns
from aayohai.socket_auth import TokenAuthMiddlewareStack
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": TokenAuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        ),
    }
)
