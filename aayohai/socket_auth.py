import os
from channels.auth import AuthMiddlewareStack
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        from accounts.models import User

        # if b'authorization' in headers:
        #     try:
        #         token_name, token_key = headers[b'authorization'].decode().split()
        #         if token_name == 'Token':
        #             token = Token.objects.get(key=token_key)
        #             scope['user'] = token.user
        #     except Token.DoesNotExist:
        #         scope['user'] = AnonymousUser()
        scope['user'] = User.objects.first()
        return await self.inner(scope, receive, send)

TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))
