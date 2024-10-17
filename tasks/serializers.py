from rest_framework import serializers
from .models import Task, TaskHistory, TaskCategory
from django.contrib.auth.models import User
from django.utils import timezone

class TaskCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCategory
        fields = '__all__'
        read_only_fields = ['user']

class TaskSerializer(serializers.ModelSerializer):
    due_date = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description',
            'due_date', 'priority', 'status',
            'user', 'completed_at', 'category',
            'recurrence', 'next_due_date', 'created_at'
        ]
        read_only_fields = ['user', 'completed_at', 'created_at']

    def validate_due_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def create(self, validated_data):
        # Get the current user from the request context
        user = self.context['request'].user

        # Assign the user to the validated_data
        validated_data['user'] = user

        # Create the task with the user field
        task = Task.objects.create(**validated_data)

        # Handle recurrence logic
        if task.recurrence and task.recurrence != 'none':
            if task.recurrence == 'daily':
                task.next_due_date = task.due_date + timezone.timedelta(days=1)
            elif task.recurrence == 'weekly':
                task.next_due_date = task.due_date + timezone.timedelta(weeks=1)
            elif task.recurrence == 'monthly':
                task.next_due_date = task.due_date + timezone.timedelta(days=30)
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

