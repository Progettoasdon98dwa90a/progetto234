import django_filters
from api.models import Employee, Branch, Role
from django import forms
from django.db.models import Q



class EmployeeFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_common_search',
        label="Cerca",  # Translatable label
        widget=forms.TextInput(attrs={
            "class": "input input-bordered",
            "placeholder": "Cerca..."  # Translatable placeholder
        })
    )
    branch = django_filters.ModelChoiceFilter(
        queryset=Branch.objects.all(),
        empty_label="Tutte",  # Translatable empty label
        label="Sede",
        widget=forms.Select(attrs={
            "class": "select select-bordered",
            'placeholder': "Tutte"
        })
    )
    role = django_filters.ModelChoiceFilter(
        queryset=Role.objects.all(),
        empty_label="Tutti",  # Translatable empty label
        label="Ruolo",
        widget=forms.Select(attrs={
            "class": "select select-bordered",
            'placeholder': "Tutti"

        })
    )

    class Meta:
        model = Employee
        fields = ['search', 'branch', 'role']

    def filter_common_search(self, queryset, name, value):
        # Custom search logic
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(branch__name__icontains=value) |
            Q(role__name__icontains=value)
        )




import django_filters
from django import forms
from api.models import Schedule, Branch
from django.db import models
from django_filters import filters

class ScheduleFilter(django_filters.FilterSet):
    branch = django_filters.ModelChoiceFilter(
        queryset=Branch.objects.all(),
        empty_label="Tutte",  # Translatable empty label
        label="Sede",
        widget=forms.Select(attrs={
            "class": "select select-bordered",
            "placeholder": "Tutte"
        })
    )
    start_date = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='exact',
        label="Data Inizio",
        widget=forms.DateInput(attrs={
            "class": "flatpickr input input-bordered",
            "placeholder": "Select start date"
        })
    )
    end_date = django_filters.DateFilter(
        field_name='end_date',  # Corrected field name!
        lookup_expr='exact',
        label="Data Fine",
        widget=forms.DateInput(attrs={
            "class": "flatpickr input input-bordered",
            "placeholder": "Select end date"
        })
    )
    id = django_filters.NumberFilter(
        field_name='id',
        lookup_expr='exact',
        widget=forms.NumberInput(attrs={
            "class": "input input-bordered",
            "placeholder": "ID",
        })
    )

    class Meta:
        model = Schedule
        # Only include the fields you want to be searchable
        fields = ['branch', 'start_date', 'end_date', 'id']

    @property
    def filter_overrides(self):
        return {
            models.JSONField: filters.CharFilter
        }