# fur_store/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from rest_framework.authtoken.views import obtain_auth_token
from drf_yasg import openapi
from accounts.views import RegistrationView

# Настройки Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Fur Store API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[]
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    path('api/register/', RegistrationView.as_view(), name='register'),
    path('api/', include('shop.urls')),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
