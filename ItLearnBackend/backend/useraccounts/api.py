from rest_framework.views import APIView
from dj_rest_auth.views import LoginView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
import logging
from django.contrib.auth.tokens import default_token_generator
from allauth.account.models import EmailAddress
from .tasks import send_reset_email
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils.encoding import force_bytes
from .serializers import PasswordResetSerializer, SetPasswordSerializer
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
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
            raise AuthenticationFailed('Unable to log in with provided credentials.')


class CustomPasswordResetAPI(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']

        user = get_object_or_404(User, email=email)

        uid = urlsafe_base64_encode(force_bytes(user.pk))  # Generate UID
        token = PasswordResetTokenGenerator().make_token(user)  # Generate Token

        reset_url = f'{settings.FRONTEND_URL}/password/reset/{uid}/{token}/'

        send_reset_email.delay(email, reset_url)
        
        return Response({"message": "Password reset email sent successfully"}, status=status.HTTP_200_OK)
    


class CustomPasswordResetConfirmAPI(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request, uidb64, token):
        try:
            # Decode the UID to get the user ID
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, User.DoesNotExist):
            return Response({"error": "Invalid token or UID."}, status=status.HTTP_401_UNAUTHORIZED)
        
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Set the new password
            user.set_password(serializer.validated_data["new_password1"])
            user.save()
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
