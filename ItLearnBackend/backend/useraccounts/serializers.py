from rest_framework import serializers
from  .models import User
import logging
from rest_framework.exceptions import ValidationError
from dj_rest_auth.registration.serializers import RegisterSerializer
from .tasks import send_confirmation_message
logger = logging.getLogger(__name__)

class CustomRegisterSerializer(RegisterSerializer):
    name = serializers.CharField(max_length=255)
    avatar = serializers.ImageField(required=False)

    def get_avatar_url(self, obj):
        return obj.avatar_url() if hasattr(obj, 'avatar_url') and obj.avatar_url() else ''
    
    def save(self, request):
        try:
            if not User.objects.filter(email=self.data.get('email')).exists():
                user = super().save(request)                
                user.name = self.data.get('name')
                
                if 'avatar' in self.data:
                    user.avatar = self.data['avatar']
                    
                user.is_active = True  # Deactivate the user until confirmation

                # Save the user with the updated fields
                user.save()

                # Trigger the task to send confirmation email
                send_confirmation_message.delay(user.id)

                return user
            else:
                raise ValidationError("A user with this email already exists.")
        except ValidationError as e:
            raise e  # Explicitly re-raise to ensure proper error response
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected error during registration: {e}")
            raise ValidationError("An unexpected error occurred. Please try again later.")
