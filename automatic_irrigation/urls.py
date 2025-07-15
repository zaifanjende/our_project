"""
URL configuration for automatic_irrigation project.

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

from django.contrib import admin
from django.urls import path, include # Make sure 'include' is imported
from django.views.generic import TemplateView # To serve simple static templates initially
from django.conf import settings # Import settings
from django.conf.urls.static import static # Import static for serving media/static files during development

urlpatterns = [
    path('admin/', admin.site.urls), # Admin panel URL
    path('', TemplateView.as_view(template_name='home.html'), name='home'), # Your new home page
    path('', include('web_app.urls')), # Include URLs from your web_app
    path('api/', include('web_app.api_urls')), 
    # You might later change 'web_app/' to '' for cleaner URLs like /register, /login etc.
    # For now, keeping it explicit for clarity.
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Note: STATIC_ROOT is typically for collectstatic in production, STATICFILES_DIRS for dev.
    # For a simple runserver, STATICFILES_DIRS is enough for dev.
    # The line above for STATIC_ROOT will work for 'collectstatic' in prod.
    # Let's also include media files if you plan to upload images etc.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

