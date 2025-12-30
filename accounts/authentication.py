from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import exceptions
import logging

logger = logging.getLogger(__name__)

User = settings.AUTH_USER_MODEL


class CookieJWTAuthentication(JWTAuthentication):
    """
    Authentication class that reads the JWT access token from Authorization header.
    Standard Bearer token authentication.
    """
    def authenticate(self, request):
        # Use the standard JWTAuthentication which reads from Authorization header
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except (InvalidToken, TokenError) as e:
            logger.warning(f"Invalid token during authentication: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {e}")
            return None

        user = self.get_user(validated_token)
        
        # Check if user is blocked
        if user and hasattr(user, 'is_block') and user.is_block:
            raise exceptions.AuthenticationFailed("Your account has been blocked. Please contact support.")
        
        return user, validated_token
