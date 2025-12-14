"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import dj_rest_auth
from dj_rest_auth import registration
from django.contrib import admin
from django.urls import path, include
from django.views.debug import default_urlconf
from drf_spectacular.contrib import rest_auth
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
import os

from fiordispino.models import genre
from fiordispino.views import LoginView, RegisterView

API_TITLE = 'fiordispino api'
API_DESCRIPTION = 'A Web Api to manage your gaming history'

urlpatterns = [

    # default home page -> otherwise disappears if you define custom routes
    path('', default_urlconf),

    # for safety reasons, save the admin mapping in the env file
    path(os.getenv('ADMIN_MAPPING'), admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    # deprecated!
    # path('docs/', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)), # human readable documentation
    # path('schema/', get_schema_view(title=API_TITLE)), # machine readable -> to generate services

    # the above are commented because deprecated, nor drf_spectacular is the standard
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # genre api
    path('api/v1/', include('fiordispino.urls')),
    path('api/v1/auth/login/', LoginView.as_view(), name='login'),
    path('api/v1/auth/registration/', RegisterView.as_view(), name='register'),
]
