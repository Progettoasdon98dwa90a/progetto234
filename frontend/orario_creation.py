import requests
from api.models import Schedule,Employee

from django.conf import settings

conn = None
cursor = None
masterplan_app = settings.MASTERPLAN_APP

def send_schedule_data_for_creation(orario_id,):
        schedule = Schedule.objects.get(id=orario_id)
        employees = Employee.objects.filter(id__in=schedule.employees).select_related('role')
        shifts_data = schedule.shift_data
        shift_types = [shift['name'] for shift in shifts_data]
        free_days = schedule.free_days

        used_roles = list(set([employee.role for employee in employees]))

        '''
        for role in used_roles:
            print(role.__dict__)

        for employee in employees:
            print(employee.__dict__)

        for shift_data in shifts_data:
            print(shift_data)

        for free_day in free_days:
            print(free_days[free_day])

        for role in used_roles:
            print("ROLE", role.__dict__)
        '''

        employees_crm = {}

        payload = {}

        roles_data = {}
        employee_data = {}
        services_data = {}

        for role in used_roles:
            role_data = {
                "title": role.name,
                "max_hours_per_day": role.max_hours_per_day,
                "max_services_per_week": role.max_services_per_week,
                "max_hours_per_week": role.max_hours_per_week,
                "max_hours_per_month": role.max_hours_per_month
            }
            roles_data[role.id] = role_data

        for employee in employees:
            employee_data[employee.id] = {
                "id": employee.id,
                "role_id": employee.role.id,
                "max_hours_per_day": employee.role.max_hours_per_day,
                "max_services_per_week": employee.role.max_services_per_week,
                "max_hours_per_week": employee.role.max_hours_per_week,
                "max_hours_per_month": employee.role.max_hours_per_month
            }

        for shift_data in shifts_data:
            service_data = {
                "name": shift_data['name'],
                "minEmployees": shift_data['minEmployees'],
                "start": shift_data['start'],
                "end": shift_data['end']
            }
            services_data[shift_data['name']] = service_data

        # Create the payload
        payload = {
            "roster_id": schedule.id,
            "roles": roles_data,
            "employees": employee_data,
            "services": services_data
        }

        # send the payload to the API

        # Define the URL for the API endpoint

        url = f"http://{masterplan_app}:7000/send_data/"

        # Send the POST request
        session = requests.Session()

        response = session.post(url, json=payload)

        print(response.status_code)









