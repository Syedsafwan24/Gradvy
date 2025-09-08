# Redirect to API URLs - this file is kept for backwards compatibility
# All auth URLs are now in api/urls.py with enhanced functionality

from django.urls import path, include

app_name = 'accounts'

urlpatterns = [
    # Redirect all auth routes to the api module
    path('', include('apps.auth.api.urls')),
]
