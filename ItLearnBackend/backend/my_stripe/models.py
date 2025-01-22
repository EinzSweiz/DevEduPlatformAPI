from django.db import models
from useraccounts.models import User

class Subscription(models.Model):
    class Subscriptions(models.TextChoices):
        FREE = 'free', 'Free'
        PRO = 'pro', 'Pro'
        ENTERPRISE = 'enterprise', 'Enterprise'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50, choices=Subscriptions, default='inactive')
    status = models.CharField(max_length=50, default='inactive')
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)  # For paid plans
    created_at = models.DateTimeField(auto_now_add=True)
