from rest_framework import serializers
from .models import Task, TaskHistory

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'due_date', 'priority', 'status', 'user', 'completed_at', 'category', 'recurrence', 'next_due_date']
        read_only_fields = ['user', 'completed_at']

class TaskHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskHistory
        fields = '__all__'