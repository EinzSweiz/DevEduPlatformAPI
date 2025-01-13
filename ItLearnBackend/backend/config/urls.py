
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from courses import urls as courses_urls
from django.conf import settings
from useraccounts import urls as useraccounts_urls


schema_view = get_schema_view(
    openapi.Info(
        title='Devdu platform API',
        default_version='v1',
        description='API Documenation for Devdu platform API',
        contact=openapi.Contact(email='riad.sultanov.1999@gmail.com'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=[],
    authentication_classes=[],
)

urlpatterns = [
    path('', include('django_prometheus.urls')),
    path('admin/', admin.site.urls),
    path('api/user/accounts/', include(useraccounts_urls)),
    path('api/courses/', include(courses_urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

