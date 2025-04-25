from django.urls import path, include

from api.views.v1.branches import get_all_branches, get_branch_employees
from api.views.v1.employees import get_all_employees, get_employee_data, manage_employee
from api.views.v1.schedules import new_schedule, get_all_schedules, schedules, schedules_employees

from api.views.v2.employees import single_employee_data
from api.views.v2.employees import set_employee_rest_days
from api.views.v2.employees import new_employee
from api.views.v2.employees import update_employee
from api.views.v2.report_branch import get_branch_report
from api.views.v2.imports import getHistory
from api.views.v2.dashboard import dashboard_data

old_urlpatterns = [
    # BRANCHES
    #ROLES

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


urlpatterns = [
    path('branches/', get_all_branches, name='get_all_branches'),

    path('import/getHistory/<int:year>/<int:branch_id>/', getHistory, name='get_history'),
    path('dashboard/<int:branch_id>/', dashboard_data, name='dashboard_data'),

    path('dipendenti/<int:branch_id>/<int:employee_id>/', single_employee_data, name='GET_EMPLOYEE_DATA'),
    path('dipendenti/<int:branch_id>/', get_branch_employees, name='GET_BRANCH_EMPLOYEES'),
    path('dipendenti/<int:branch_id>/createEmployee/', new_employee, name='CREATE_EMPLOYEE'),
    path('dipendenti/<int:branch_id>/updateEmployee/<int:employee_id>/', update_employee, name='UPDATE_EMPLOYEE'),
    path('<int:branch_id>/report/branch/', get_branch_report, name='GET_BRANCH_REPORT'),
    path('dipendenti/<int:branch_id>/updateEmployeeRestDays/<int:employee_id>/', set_employee_rest_days,
         name='SET_EMPLOYEE_REST_DAYS')

]


