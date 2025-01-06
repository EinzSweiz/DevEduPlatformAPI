from rest_framework.views import APIView
from dj_rest_auth.views import LoginView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
import logging
logger = logging.getLogger(__name__)


class CustomLoginAPI(LoginView):
    authentication_classes = []
    permission_classes = [  ]
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            user = self.user
            if not user.is_verified:
                raise AuthenticationFailed("E-mail is not verified.")
            return response
        except AuthenticationFailed as e:
            raise e
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            raise AuthenticationFailed("An unexpected error occurred during login. Please try again.")
