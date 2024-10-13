from django.urls import path
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    TaskListCreateView,
    TaskRetrieveUpdateDestroyView,
    UserLoginView,
    UserRegistrationView,
    TaskHistoryView
)

app_name = 'tasks'  # Required for namespacing URLs in the main urls.py

urlpatterns = [
    # API documentation and schema
    path('', get_schema_view(title="Task Manager API", description="API for task management"), name='api-root'),
    path('docs/', include_docs_urls(title="Task Manager API"), name='api-docs'),
    path('login/', UserLoginView.as_view(), name='user-login'),

    # API endpoints for tasks
    path('v1/tasks/', TaskListCreateView.as_view(), name='task-list-create'),  # List and create tasks
    path('v1/tasks/<int:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='task-detail'),  # Retrieve, update, or delete a task
    path('v1/tasks/<int:task_id>/history/', TaskHistoryView.as_view(), name='task-history'),  # Get task history

    # Authentication endpoints
    path('v1/register/', UserRegistrationView.as_view(), name='user-register'),  # User registration
    path('v1/login/', obtain_auth_token, name='api-token-auth'),  # Token authentication
]