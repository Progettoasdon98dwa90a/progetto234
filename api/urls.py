
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    # BRANCHES
    path('branches/', views.get_all_branches, name='get_all_branches'),
    #ROLES
    path('roles/', views.get_all_roles, name='get_all_roles'),

    # EMPLOYEES
    path('all_employees/', views.get_all_employees, name='get_all_employees'),
    path('employee_data/<int:employee_id>', views.get_employee_data, name='get_employee_data'),
    path('manage_employee/', views.manage_employee, name='manage_employee'),
    path('get_branch_employees/<int:branch_id>', views.get_branch_employees, name='get_branch_employees'),

    # SCHEDULES
    path('new_schedule/', views.new_schedule, name='new_schedule'),
    path('schedules/all/', views.get_all_schedules, name='get_all_schedules'),
    path('schedules/<int:schedule_id>', views.schedules, name='schedules' ),
    path('schedules/<int:schedule_id>/employees', views.schedules_employees, name='schedules_employees'),
]
