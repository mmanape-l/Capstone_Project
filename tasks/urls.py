from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.schemas import get_schema_view
from .views import (
    TaskViewSet,
    UserViewSet,
    TaskHistoryView,
    UserLoginView,
    UserLogoutView,
    NotificationView,
    TaskCategoryViewSet,
    RecurringTaskViewSet,
)

app_name = 'tasks'

# Initialize the router for viewsets
router = DefaultRouter()

# Register viewsets with the router
router.register('tasks', TaskViewSet, basename='task')
router.register('users', UserViewSet, basename='user')
router.register('categories', TaskCategoryViewSet, basename='category')
router.register('recurring-tasks', RecurringTaskViewSet, basename='recurring-task')

# API Endpoints
urlpatterns = [
    # Authentication endpoints
    path('token/', obtain_auth_token, name='token_obtain'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    # API root and documentation
    path('', get_schema_view(
        title="Task Manager API",
        description="API for comprehensive task management",
        version="1.0.0"
    ), name='api-root'),

    # Include all router URLs
    path('', include(router.urls)),

    # Custom endpoints for specific task operations
    path('tasks/<int:task_id>/history/',
         TaskHistoryView.as_view(),
         name='task-history'),
    path('tasks/<int:task_id>/toggle-complete/',
         TaskViewSet.as_view({'post': 'toggle_complete'}),
         name='task-toggle-complete'),
    path('tasks/<int:task_id>/share/',
         TaskViewSet.as_view({'post': 'share_task'}),
         name='share-task'),

    # Notifications endpoint
    path('notifications/',
         NotificationView.as_view(),
         name='notifications'),
]

