from rest_framework.views import APIView
from dj_rest_auth.views import LoginView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
import logging
from django.contrib.auth.tokens import default_token_generator
from allauth.account.models import EmailAddress
from .tasks import send_reset_email, send_useraccount_changes_message
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils.encoding import force_bytes
from .serializers import PasswordResetSerializer, SetPasswordSerializer, UserModelDynamicSerializer
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from .swagger_usecases import email_schema, login_request_body, login_responses, profile_update_params, profile_schema, password_reset_schema
from .models import User
from .mixins import ParserMixinAPI

logger = logging.getLogger('default')

class ConfirmEmailView(APIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_description="Confirm a user's email with the provided token and user ID.",
        responses={
            200: openapi.Response("Email confirmed successfully"),
            400: openapi.Response("Invalid or expired token"),
            404: openapi.Response("User not found"),
        },
    )
    def get(self, request, user_id, token):
        logger.info(f"Email confirmation requested for user_id={user_id}")
        try:
            user = User.objects.get(pk=user_id)
            if not default_token_generator.check_token(user, token):
                logger.warning(f"Invalid token for user_id={user_id}")
                return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

            # Mark email as verified
            user.is_active = True
            user.is_verified = True
            user.save()

            email = EmailAddress.objects.get(user=user)
            email.verified = True
            email.save()
            logger.info(f"Email verified for user_id={user_id}")

            return Response({"message": "Email confirmed successfully"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            logger.error(f"User not found: user_id={user_id}")
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error during email confirmation: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginAPI(LoginView):
    authentication_classes = []
    permission_classes = []
    

    @swagger_auto_schema(
        operation_description="User login endpoint",
        request_body=login_request_body,
        responses=login_responses,
    )
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            user = self.user
            if not user.is_verified:
                raise AuthenticationFailed("E-mail is not verified.")
            data = response.data
            data['is_deleted'] = user.is_deleted
            return Response(data)
        except AuthenticationFailed as e:
            raise e
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            raise AuthenticationFailed('Unable to log in with provided credentials.')


class CustomPasswordResetAPI(APIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_description="Send password reset email (JSON format).",
        request_body=email_schema,  # Use the reusable schema for JSON input
        responses={
            200: openapi.Response("Password reset email sent successfully."),
            400: openapi.Response("Invalid data"),
            404: openapi.Response("User not found"),
        },
    )
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

    @swagger_auto_schema(
        operation_description="Reset the password using a token and UID (JSON format).",
        request_body=password_reset_schema,  # Use the reusable schema for JSON input
        responses={
            200: openapi.Response("Password reset successfully.", schema=password_reset_schema),
            401: openapi.Response("Invalid token or UID"),
            400: openapi.Response("Invalid data"),
        },
    )
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
        

class ProfileDetailViewAPI(ParserMixinAPI, APIView):
    FIELDS = [
        'email', 'name', 'avatar', 'avatar_url', 'bio', 'location',
        'phone_number', 'linkedin', 'github', 'subscription_plan',
        'subscription_start_date', 'subscription_end_date',
        'is_subscription_active', 'is_deleted',
    ]


    @swagger_auto_schema(
        operation_description="Retrieve user profile details.",
        responses={200: profile_schema, 401: "Not authenticated"}
    )
    def get(self, request):
        user = request.user
        serializer = UserModelDynamicSerializer(user, fields=self.FIELDS)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update user profile details.",
        manual_parameters=profile_update_params,  # Use the reusable parameters for profile update
        responses={200: profile_schema, 400: "Invalid data"}
    )
    def put(self, request):
        user = request.user

        serializer = UserModelDynamicSerializer(
            user,
            data=request.data,
            partial=True,
            fields=self.FIELDS,
        )

        if serializer.is_valid():
            serializer.save()
            send_useraccount_changes_message.delay(user.id)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
