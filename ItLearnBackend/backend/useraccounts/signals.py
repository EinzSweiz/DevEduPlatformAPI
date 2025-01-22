import stripe
from django.conf import settings
from django.db.models.signals import post_save
from .models import User
from django.dispatch import receiver
import logging

# Set up Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

def create_stripe_customer(user):
    """
    Creates a Stripe customer for the given user if it doesn't already exist.
    """
    try:
        if not user.stripe_customer_id:
            # Create a new Stripe customer
            customer = stripe.Customer.create(
                email=user.email,
                name=user.name
            )
            user.stripe_customer_id = customer.id
            # Save the updated user instance
            user.save(update_fields=['stripe_customer_id'])
            logger.info(f"Stripe customer created successfully for user {user.email}")
        return user.stripe_customer_id
    except Exception as e:
        logger.error(f"Failed to create Stripe customer for user {user.email}: {e}")
        return None


@receiver(post_save, sender=User)
def create_customer_signal(sender, instance, created, **kwargs):
    """
    Signal to create a Stripe customer when a new User instance is created.
    """
    if created:
        logger.info(f"Creating Stripe customer for new user: {instance.email}")
        create_stripe_customer(instance)
