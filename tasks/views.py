from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Task, TaskHistory, Notification
from .serializers import TaskSerializer, TaskHistorySerializer
from django_filters import rest_framework as filters
from rest_framework import filters as drf_filters
from datetime import timedelta
from django.utils import timezone

class TaskFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status', lookup_expr='exact')
    priority = filters.CharFilter(field_name='priority', lookup_expr='exact')
    due_date = filters.DateFilter(field_name='due_date', lookup_expr='lte')

    class Meta:
        model = Task
        fields = ['status', 'priority', 'due_date']

class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend, drf_filters.OrderingFilter)
    filterset_class = TaskFilter
    ordering_fields = ['due_date', 'priority']
    ordering = ['due_date']

    def perform_create(self, serializer):
        task = serializer.save(user=self.request.user)
        
        # Log task creation in TaskHistory
        TaskHistory.objects.create(task=task, action='created', details=f'Task "{task.title}" created.')

        if task.due_date and task.due_date <= timezone.now() + timedelta(days=2):  # Notify if due in 2 days
            Notification.objects.create(
                user=self.request.user,
                task=task,
                message=f"Task '{task.title}' is due soon!"
            )
        
        # Handle recurring tasks
        if task.recurrence and task.recurrence != 'None':
            if task.recurrence == 'Daily':
                task.next_due_date = task.due_date + timedelta(days=1)
            elif task.recurrence == 'Weekly':
                task.next_due_date = task.due_date + timedelta(weeks=1)
            elif task.recurrence == 'Monthly':
                task.next_due_date = task.due_date + timedelta(weeks=4)  # Approximation for a month
            
            task.save()

class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_update(self, serializer):
        task = serializer.save()
        # Log task update in TaskHistory
        TaskHistory.objects.create(task=task, action='updated', details=f'Task "{task.title}" updated.')

    def perform_destroy(self, instance):
        # Log task deletion in TaskHistory before deleting the task
        TaskHistory.objects.create(task=instance, action='deleted', details=f'Task "{instance.title}" deleted.')
        instance.delete()

class TaskHistoryView(generics.ListAPIView):  # Updated the class name for consistency
    serializer_class = TaskHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        # Retrieve task history for the given task owned by the logged-in user
        return TaskHistory.objects.filter(task__id=task_id, task__user=self.request.user)

class UserRegistrationView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        token = Token.objects.create(user=user)

        return Response({'token': token.key}, status=status.HTTP_201_CREATED)
