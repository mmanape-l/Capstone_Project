from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # API endpoints - All API routes are prefixed with 'api/'
    path('api/', include('tasks.urls', namespace='tasks')),

    # API Documentation - Available at '/docs/'
    path('docs/', include_docs_urls(
        title="Task Manager API",
        description="API documentation for the Task Manager application"
    )),

    # Authentication endpoints
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Redirect root URL to API documentation for better UX
    path('', RedirectView.as_view(url='/docs/', permanent=False)),
]

# Static and media files configuration for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)