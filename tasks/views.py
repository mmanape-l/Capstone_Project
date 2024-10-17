from rest_framework import viewsets, generics, permissions, status, filters as drf_filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from datetime import timedelta
from .models import Task, TaskHistory, Notification, TaskCategory
from .serializers import TaskSerializer, TaskHistorySerializer, UserSerializer, TaskCategorySerializer

class TaskHistoryView(generics.ListAPIView):
    """
    View for retrieving task history.
    """
    serializer_class = TaskHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        return TaskHistory.objects.filter(
            task_id=task_id,
            task__user=self.request.user
        ).order_by('-created_at')

class RecurringTaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing recurring tasks.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            user=self.request.user,
            recurrence__isnull=False
        ).exclude(recurrence='none')

class TaskCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing task categories.
    """
    serializer_class = TaskCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TaskCategory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TaskFilter(filters.FilterSet):
    """Filter class for Tasks"""
    status = filters.CharFilter(field_name='status', lookup_expr='exact')
    priority = filters.CharFilter(field_name='priority', lookup_expr='exact')
    due_date = filters.DateFilter(field_name='due_date', lookup_expr='lte')
    category = filters.CharFilter(field_name='category__name', lookup_expr='icontains')

    class Meta:
        model = Task
        fields = ['status', 'priority', 'due_date', 'category']

class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend, drf_filters.OrderingFilter, drf_filters.SearchFilter)
    filterset_class = TaskFilter
    ordering_fields = ['due_date', 'priority', 'created_at']
    ordering = ['due_date']
    search_fields = ['title', 'description']

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            task = serializer.save(user=self.request.user)

            # Create task history entry
            TaskHistory.objects.create(
                task=task,
                action='created',
                details=f'Task "{task.title}" created.'
            )

            # Create notification if task is due soon
            if task.due_date and task.due_date <= timezone.now() + timedelta(days=2):
                Notification.objects.create(
                    user=self.request.user,
                    task=task,
                    message=f"Task '{task.title}' is due soon!"
                )

            # Handle recurring tasks
            if task.recurrence and task.recurrence != 'none':
                self._handle_recurrence(task)

        except Exception as e:
            raise ValidationError(f"Failed to create task: {str(e)}")

    def _handle_recurrence(self, task):
        """Handle recurring task logic"""
        recurrence_map = {
            'daily': timedelta(days=1),
            'weekly': timedelta(weeks=1),
            'monthly': timedelta(days=30),
        }

        if task.recurrence.lower() in recurrence_map:
            task.next_due_date = task.due_date + recurrence_map[task.recurrence.lower()]
            task.save()

    @action(detail=True, methods=['post'])
    def toggle_complete(self, request, pk=None):
        task = self.get_object()
        task.status = 'PENDING' if task.status == 'COMPLETED' else 'COMPLETED'
        task.completed_at = timezone.now() if task.status == 'COMPLETED' else None
        task.save()

        TaskHistory.objects.create(
            task=task,
            action='status_changed',
            details=f'Task status changed to {task.status}'
        )

        return Response({'status': task.status})

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management"""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = serializer.save()
        Token.objects.create(user=user)

class UserLoginView(ObtainAuthToken):
    """Custom login view with renderer classes"""
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class UserLogoutView(APIView):
    """Handle user logout"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out'},
                          status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)},
                          status=status.HTTP_400_BAD_REQUEST)

class NotificationView(generics.ListAPIView):
    """View for user notifications"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(user=request.user)
        data = [{
            'message': notification.message,
            'task': notification.task.title,
            'created': notification.created,
            'is_read': notification.is_read
        } for notification in notifications]
        return Response(data)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})


def get_serializer_context(self):
    context = super().get_serializer_context()
    context.update({"request": self.request})
    return context