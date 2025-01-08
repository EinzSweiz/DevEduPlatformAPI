from rest_framework import serializers
from .models import User
import logging
from rest_framework.exceptions import ValidationError
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.password_validation import validate_password
from .tasks import send_confirmation_message

logger = logging.getLogger(__name__)

class CustomRegisterSerializer(RegisterSerializer):
    name = serializers.CharField(max_length=255)
    avatar = serializers.ImageField(required=False)
    def validate_password1(self, value):
        """
        Add custom password validation logic here if needed.
        This method is called automatically by Django REST Framework.
        """
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if value.isdigit():
            raise serializers.ValidationError("Password cannot be entirely numeric.")
        return value

    def validate_email(self, value):
        """
        Add custom email validation logic here if needed.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def save(self, request):
        try:
            user = super().save(request)
            user.name = self.data.get('name')

            if 'avatar' in self.data:
                user.avatar = self.data['avatar']

            user.is_active = True  # Activate the user immediately
            user.save()

            # Trigger the task to send a confirmation email
            send_confirmation_message.delay(user.id)

            return user
        except ValidationError as e:
            raise e  # Re-raise validation errors
        except Exception as e:
            logger.error(f"Unexpected error during registration: {e}")
            raise ValidationError("An unexpected error occurred. Please try again later.")


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class SetPasswordSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password1 = attrs.get("new_password1")  # Correct field name
        password2 = attrs.get("new_password2")  # Correct field name

        if password1 != password2:
            raise serializers.ValidationError("Passwords do not match.")
        
        validate_password(password1)
        return attrs