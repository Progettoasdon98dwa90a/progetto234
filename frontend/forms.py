from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from api.models import Employee, Schedule


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'branch', 'role']


class ScheduleForm(forms.ModelForm):
    """
    This form uses a ModelMultipleChoiceField (`employees_select`) for user selection,
    then converts it into a list of IDs for the JSONField (`employees`).
    """

    # This is your "UI field" for multiple selection
    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select select-bordered w-full'}),
        required=False,
        label="Dipendenti"
    )
    # Checkbox for "Tutti i dipendenti"
    allEmployees = forms.BooleanField(required=False, label="Tutti i dipendenti")

    class Meta:
        model = Schedule
        # Note: 'employees' is not listed in fields because we handle it manually
        fields = ['start_date', 'end_date', 'branch', "employees"]

        widgets = {
            'start_date': forms.DateInput(
                attrs={
                    'class': 'flatpickr input input-bordered',
                    'autocomplete': 'off'
                }
            ),
            'end_date': forms.DateInput(
                attrs={
                    'class': 'flatpickr input input-bordered',
                    'autocomplete': 'off'
                }
            ),
            'branch': forms.Select(attrs={'class': 'select select-bordered w-full'}),
        }

    def clean(self):
        """
        Convert the selected employees into a Python list of IDs
        so we can store them in the JSONField.
        """
        cleaned_data = super().clean()

        # If 'allEmployees' is checked, handle that logic here,
        # or you can do it in the view. For example:
        all_emp_flag = cleaned_data.get('allEmployees')
        branch = cleaned_data.get('branch')

        if all_emp_flag and branch:
            # Override any selected employees with all in that branch
            emp_ids = list(Employee.objects.filter(branch=branch).values_list('id', flat=True))
            cleaned_data['employees'] = Employee.objects.filter(id__in=emp_ids)

        # Convert the selected employees to a list of IDs
        employees_qs = cleaned_data.get('employees')  # This is a QuerySet of Employees
        if employees_qs:
            employees_list = [e.id for e in employees_qs]
        else:
            employees_list = []

        # Assign this list to a new key in cleaned_data for saving.
        cleaned_data['employees'] = employees_list
        return cleaned_data

    def save(self, commit=True):
        """
        Overwrite the model's JSONField with the cleaned list of IDs.
        """
        instance = super().save(commit=False)
        # `employees` is your JSONField on the model
        instance.employees = self.cleaned_data['employees']  # A Python list of IDs

        if commit:
            instance.save()

        return instance




