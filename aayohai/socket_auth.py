import os
import jwt

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from channels.auth import AuthMiddlewareStack

from accounts.models import User

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


class TokenAuthMiddleware:
    """
    Custom middleware for JWT authentication in Django Channels.
    """

    def __init__(self, inner):
        self.inner = inner

    def _get_authorization_header(self, scope):
        """
        Helper to extract the Authorization header as a string.
        """
        headers = dict(scope.get('headers', []))
        auth_header = headers.get(b'authorization')
        if auth_header:
            return auth_header.decode('utf-8')
        return None

    def authenticate_token(self, token):
        """
        Verifies the JWT token and returns the authenticated User or None.
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            user_id = payload.get('user_id')
            if user_id is None:
                return None

            user = User.objects.filter(id=user_id).first()
            if user and user.is_active:
                return user

        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.InvalidTokenError:
            # Token is invalid in general
            return None

        return None

    async def __call__(self, scope, receive, send):
        auth_header = self._get_authorization_header(scope)

        user = AnonymousUser()

        if auth_header:
            parts = auth_header.split(' ')
            if len(parts) == 2 and parts[0].lower() == 'jwt':
                token = parts[1]
                user_obj = self.authenticate_token(token)
                if user_obj:
                    user = user_obj

        scope['user'] = user

        return await self.inner(scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    """
    Factory function for easy middleware stacking.
    """
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))
