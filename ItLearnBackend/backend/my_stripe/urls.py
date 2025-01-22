from django.urls import path
from . import api

urlpatterns = [
    path('payment/success/', api.PaymentSuccessAPI.as_view(), name='api_payment_success'),
    path('payment/cancel/<uuid:pk>/', api.PaymentCancel.as_view(), name='api_payment_cancel'),
    path('stripe_webhook/', api.StripeWebhook.as_view(), name='stripe_webhook'),
    path('webhook/', api.StripeWebhook.as_view(), name='api_webhook')
]