from rest_framework import generics, permissions, status, filters as drf_filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.utils import timezone
from django_filters import rest_framework as filters
from datetime import timedelta
from .models import Task, TaskHistory, Notification
from .serializers import TaskSerializer, TaskHistorySerializer, UserSerializer

class TaskFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status', lookup_expr='exact')
    priority = filters.CharFilter(field_name='priority', lookup_expr='exact')
    due_date = filters.DateFilter(field_name='due_date', lookup_expr='lte')

    class Meta:
        model = Task
        fields = ['status', 'priority', 'due_date']

class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]  # Changed to IsAuthenticated
    filter_backends = (filters.DjangoFilterBackend, drf_filters.OrderingFilter)
    filterset_class = TaskFilter
    ordering_fields = ['due_date', 'priority']
    ordering = ['due_date']

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        task = serializer.save(user=self.request.user)
        TaskHistory.objects.create(task=task, action='created', details=f'Task "{task.title}" created.')

        if task.due_date and task.due_date <= timezone.now() + timedelta(days=2):
            Notification.objects.create(
                user=self.request.user,
                task=task,
                message=f"Task '{task.title}' is due soon!"
            )

        if task.recurrence and task.recurrence != 'None':
            self.handle_recurrence(task)

    def handle_recurrence(self, task):
        if task.recurrence == 'Daily':
            task.next_due_date = task.due_date + timedelta(days=1)
        elif task.recurrence == 'Weekly':
            task.next_due_date = task.due_date + timedelta(weeks=1)
        elif task.recurrence == 'Monthly':
            task.next_due_date = task.due_date + timedelta(days=30)

        task.save()

class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        task = serializer.save()
        TaskHistory.objects.create(task=task, action='updated', details=f'Task "{task.title}" updated.')

    def perform_destroy(self, instance):
        TaskHistory.objects.create(task=instance, action='deleted', details=f'Task "{instance.title}" deleted.')
        instance.delete()

class TaskHistoryView(generics.ListAPIView):
    serializer_class = TaskHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        return TaskHistory.objects.filter(task__id=task_id, task__user=self.request.user)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        Token.objects.create(user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        token = Token.objects.get(user__username=serializer.data['username'])
        return Response({'token': token.key}, status=status.HTTP_201_CREATED, headers=headers)

# Add this new view for user login
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

class UserLoginView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
