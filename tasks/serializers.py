from rest_framework import serializers
from .models import Task, TaskHistory
from django.contrib.auth.models import User
from django.utils import timezone

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description',
            'due_date', 'priority', 'status',
            'user', 'completed_at', 'category',
            'recurrence', 'next_due_date'
        ]
        read_only_fields = ['user', 'completed_at']

    def validate_due_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def create(self, validated_data):
        task = Task.objects.create(**validated_data)
        # Handle recurrence logic here if needed
        if task.recurrence and task.recurrence != 'None':
            if task.recurrence == 'Daily':
                task.next_due_date = task.due_date + timezone.timedelta(days=1)
            elif task.recurrence == 'Weekly':
                task.next_due_date = task.due_date + timezone.timedelta(weeks=1)
            elif task.recurrence == 'Monthly':
                task.next_due_date = task.due_date + timezone.timedelta(days=30)  # More accurate than 4 weeks
            task.save()
        return task

class TaskHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskHistory
        fields = '__all__'  # Consider specifying fields for better control

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user