class TaskFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status', lookup_expr='exact')
    priority = filters.CharFilter(field_name='priority', lookup_expr='exact')
    due_date = filters.DateFilter(field_name='due_date', lookup_expr='lte')
    category = filters.CharFilter(field_name='category', lookup_expr='exact')  # New filter

    class Meta:
        model = Task
        fields = ['status', 'priority', 'due_date', 'category']  # Include category
