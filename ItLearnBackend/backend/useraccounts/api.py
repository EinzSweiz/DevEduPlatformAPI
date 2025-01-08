from rest_framework.views import APIView
from dj_rest_auth.views import LoginView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
import logging
from django.contrib.auth.tokens import default_token_generator
from allauth.account.models import EmailAddress
from rest_framework import status
from .models import User

logger = logging.getLogger(__name__)

class ConfirmEmailView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request, user_id, token):
        try:
            # Verify user exists
            user = User.objects.get(pk=user_id)

            # Check if the token is valid
            if not default_token_generator.check_token(user, token):
                return Response(
                    {"error": "Invalid or expired token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Activate the user and mark the email as verified
            user.is_active = True
            user.is_verified = True
            user.save()

            email = EmailAddress.objects.get(user=user)
            email.verified = True
            email.save()

            return Response(
                {"message": "Email confirmed successfully"},
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except EmailAddress.DoesNotExist:
            return Response(
                {"error": "Email address not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

class CustomLoginAPI(LoginView):
    authentication_classes = []
    permission_classes = []
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
