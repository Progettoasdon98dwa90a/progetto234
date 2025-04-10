
from django.contrib import admin
from django.urls import path, include

from api.views.branches import get_all_branches, get_branch_employees
from api.views.roles import get_all_roles
from api.views.employees import get_all_employees, get_employee_data, manage_employee
from api.views.schedules import new_schedule, get_all_schedules, schedules, schedules_employees
from api import views


urlpatterns = [
    # BRANCHES
    path('branches/', get_all_branches, name='get_all_branches'),
    #ROLES
    path('roles/', get_all_roles, name='get_all_roles'),

    # EMPLOYEES
    path('all_employees/', get_all_employees, name='get_all_employees'),
    path('employee_data/<int:employee_id>', get_employee_data, name='get_employee_data'),
    path('manage_employee/', manage_employee, name='manage_employee'),
    path('get_branch_employees/<int:branch_id>', get_branch_employees, name='get_branch_employees'),

    # SCHEDULES
    path('new_schedule/', new_schedule, name='new_schedule'),
    path('schedules/all/', get_all_schedules, name='get_all_schedules'),
    path('schedules/<int:schedule_id>', schedules, name='schedules' ),
    path('schedules/<int:schedule_id>/employees', schedules_employees, name='schedules_employees'),
]

