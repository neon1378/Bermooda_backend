from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import UntypedToken
from django.contrib.auth.models import AnonymousUser
from UserManager.models import UserAccount
from jwt import decode as jwt_decode
from django.conf import settings
from WorkSpaceManager.models import  WorkSpace,WorkspaceMember
from jwt import decode as jwt_decode, InvalidTokenError
@database_sync_to_async
def get_user(token_key):
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        try:
            token_key = (dict((x.split('=') for x in scope['query_string'].decode().split("&")))).get('token', None)
        except ValueError:
            token_key = None
        scope['user'] = AnonymousUser() if token_key is None else await get_user(token_key)
        return await super().__call__(scope, receive, send)
    








# class JWTAuthMiddleware:
#     """Middleware for JWT authentication in WebSocket connections."""
#
#     def __init__(self, inner):
#         self.inner = inner
#
#     async def __call__(self, scope, receive, send):
#         # Parse token from query string
#         query_string = parse_qs(scope['query_string'].decode())
#         token = query_string.get('token', [None])[0]
#
#         # Default to AnonymousUser
#         scope['user'] = AnonymousUser()
#
#         if token:
#             try:
#                 # Decode JWT token
#                 decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
#                 user_id = decoded_data.get('user_id')
#                 user_detail = await  self.get_user(user_id)
#                 # Fetch user object from the database
#                 scope['user'] = user_detail.get('user')
#                 print(scope['user'],"@@")
#             except (InvalidTokenError, UserAccount.DoesNotExist):
#                 # Invalid token or user not found, keep user as AnonymousUser
#                 pass
#
#         return await self.inner(scope, receive, send)
#
#     @database_sync_to_async
#     def get_user(self, user_id):
#         user_account =UserAccount.objects.get(id=user_id)
#
#
#         return {
#             "user":user_account,
#
#
#         }


class JWTAuthMiddleware:
    """Middleware for JWT and Token authentication in WebSocket connections."""

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        from urllib.parse import parse_qs
        from django.contrib.auth.models import AnonymousUser
        from rest_framework.authtoken.models import Token
        from jwt import decode as jwt_decode, InvalidTokenError
        from django.conf import settings

        # Parse token from query string
        query_string = parse_qs(scope['query_string'].decode())
        token = query_string.get('token', [None])[0]

        # Default to AnonymousUser
        scope['user'] = AnonymousUser()

        if token:
            # First try JWT token
            try:
                decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = decoded_data.get('user_id')
                user_detail = await self.get_user(user_id)
                scope['user'] = user_detail.get('user')
                return await self.inner(scope, receive, send)
            except InvalidTokenError:
                pass  # Try the next method

            # Then try DRF TokenAuthentication
            try:
                user_detail = await self.get_user_by_drf_token(token)
                scope['user'] = user_detail.get('user')
            except Token.DoesNotExist:
                pass

        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        from UserManager.models import UserAccount
        user_account = UserAccount.objects.get(id=user_id)
        return {"user": user_account}

    @database_sync_to_async
    def get_user_by_drf_token(self, token):
        from UserManager.models import UserAccount
        from rest_framework.authtoken.models import Token
        token_obj = Token.objects.select_related('user').get(key=token)
        return {"user": token_obj.user}
