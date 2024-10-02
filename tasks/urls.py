from django.urls import path
from .views import TaskListCreateView, TaskRetrieveUpdateDestroyView, UserRegistrationView, TaskHistoryView

urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='task-detail'),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('tasks/<int:task_id>/history/', TaskHistoryView.as_view(), name='task-history'),
]
