from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
import logging

logger = logging.getLogger(__name__)

class CookiesJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            return None
        try:
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token=validated_token)
            return (user, validated_token)
        except InvalidToken as e:
            logger.warning(f"Invalid token received: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in token validation: {e}")
            return None
