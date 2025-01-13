from celery import shared_task
from helpers.messaging import send_message
from .models import User
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from decouple import config
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)

ADMIN_USER_EMAIL = config('ADMIN_USER_EMAIL', cast=str, default=None)

@shared_task
def send_confirmation_message(user_id):
    try:
        user = User.objects.get(pk=user_id)
        token = default_token_generator.make_token(user)
        confirmation_url = f"{settings.FRONTEND_URL}/email-confirmation?uid={user.id}&token={token}"
        
        subject = 'Please confirm your email address'
        message = (
            f"Hi {user.name},\n\n"
            f"Please confirm your email address by clicking the link below:\n"
            f"{confirmation_url}\n\n"
            f"Thank you!"
        )
        
        send_message(subject, message, ADMIN_USER_EMAIL, user.email)
    except Exception as e:
        logger.log(f"Error sending confirmation email: {e}")

    



@shared_task
def send_reset_email(email, reset_url):
    subject = "Reset Your Password - http://localhost:3000"
    
    # HTML version of the email message
    message = f"""
    <html>
    <body>
        <h2>Password Reset Request</h2>
        <p>Hello,</p>
        <p>We received a request to reset your password for your account associated with this email address.</p>
        <p>You can reset your password by clicking the link below:</p>
        <a href="{reset_url}" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">Reset Password</a>
        <p>If you did not request this, no further action is required. However, we recommend that you secure your account if you suspect any unauthorized access.</p>
        <p>This link will expire in 24 hours.</p>
        <p>Thank you for using our service.</p>
        <p>Best regards,</p>
        <p>The Your App Name Team</p>
        <p><a href="mailto:support@coursesIT.com">support@coursesIT.com</a></p>
    </body>
    </html>
    """
    
    # Send the email with HTML content
    send_message(
        subject,          # Subject of the email
        '',               # Plain text message (leave empty since we are sending HTML)
        ADMIN_USER_EMAIL,       # Sender email address
        email,          # Recipient email address
        html_message=message  # HTML version of the message
    )

@shared_task
def send_useraccount_changes_message(user_id):
    try:
        user = get_object_or_404(User, pk=user_id)
        subject = "Account Changes Notification - Courses IT App"
        
        # HTML version of the email message
        html_message = f"""
        <html>
        <body>
            <h2>Account Changes Notification</h2>
            <p>Hello <strong>{user.name}</strong>,</p>
            <p>We noticed changes were made to your account. If you did not perform these changes, please take immediate action to secure your account and contact our support team.</p>
            <p>If you made these changes, no further action is required.</p>
            <p>Thank you for being a valued user of our platform.</p>
            <p>Best regards,<br>The Your App Name Team</p>
            <p>Support: <a href="mailto:support@yourapp.com">support@yourapp.com</a></p>
        </body>
        </html>
        """
        
        # Plain text version of the email
        plain_message = (
            f"Hello {user.name},\n\n"
            f"We noticed changes were made to your account. If you did not perform these changes, please take immediate action to secure your account and contact our support team.\n\n"
            f"If you made these changes, no further action is required.\n\n"
            f"Thank you for being a valued user of our platform.\n\n"
            f"Best regards,\n"
            f"The Your App Name Team\n"
            f"Support: support@yourapp.com"
        )
        
        # Send the email with both plain text and HTML versions
        send_message(
            subject=subject,
            message='',
            from_email=ADMIN_USER_EMAIL,
            to_email=user.email,
            html_message=html_message
        )
    except Exception as e:
        logger.error(f"Error sending account changes email to user {user_id}: {e}")
