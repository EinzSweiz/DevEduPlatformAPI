from django.urls import path
from .api import CustomLoginAPI, ConfirmEmailView
from dj_rest_auth.registration.views import RegisterView
from .serializers import CustomRegisterSerializer
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/', CustomLoginAPI.as_view(), name='users_login_api'),
    path('register/', RegisterView.as_view(serializer_class=CustomRegisterSerializer), name='users_regiter_api'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('<uuid:user_id>/<token>/', ConfirmEmailView.as_view(), name='confirm_email_api')
]