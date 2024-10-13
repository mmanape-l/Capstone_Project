from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # API URLs with namespace 'tasks'
    path('api/', include('tasks.urls', namespace='tasks')),

    # API documentation
    path('docs/', include_docs_urls(title="Task Manager API")),

    # Redirect root URL to API root
    path('', RedirectView.as_view(url='/api/', permanent=False)),

    # Django Rest Framework built-in auth views
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Serve static and media files in development
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
