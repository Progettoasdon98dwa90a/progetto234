import json

from django.http import JsonResponse
from datetime import datetime, timedelta

from django.views.decorators.csrf import csrf_exempt

from api.models import Employee
from api.formulas.receipts import get_scontrini_dipendente_date_range

def single_employee_data(request, branch_id, employee_id):
    employee, branch = None, None

    # Calculate fallback to the last 30 days
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()

    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    try:
        employee_id = int(employee_id)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid employee ID'})

    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Employee not found'})

    dipendente_schema = {
        "id": employee.id,
        "employeeInfo": {
            "name": employee.first_name,
            "surname": employee.last_name,
            "genre": employee.genre,  # Enum numerico (es. 0=Non specificato, 1=Maschio, 2=Femmina)
            "birthDate": employee.birth_date,
            "telNumber": employee.phone_number,
            "email": employee.email,
        },
        "employeeContract": {
            "role": employee.role,
            "class": employee.skill_class,
            "branch": branch_id,  # ID numerico della sede
            "contract": employee.contract_type,  # Valori possibili da TipoContratto (non specificato nell'originale)
            "monthlyHour": employee.max_hours_per_month,
            "hourlyCost": employee.hourly_cost,
            "contractStart": employee.contract_start,
            "contractEnd": employee.contract_end,
        },
        "restDays": [0,1],  # Valori possibili: 0= Lunedi, 1=Martedi, 2=Mercoledi, 3=Giovedi, 4=Venerdi, 5=Sabato, 6=Domenica
        "holydays": [],  # Array di oggetti Ferie (struttura non specificata nell'originale)
        "workedHours": {
            "worked": "",
            "total": ""
        }, # capire se fare fallback su ultimi 30 gg
        "salesData": {
            "mediumReceiptValue": get_scontrini_dipendente_date_range(employee_id, start_date_str, end_date_str),  # Oggetto Metrica non definito nell'originale
            "mediumReceiptCount": {},
            "mediumPiecesReceipt": {},
            "startDate": None,
            "endDate": None
        }
    }

    return JsonResponse(dipendente_schema)


@csrf_exempt
def new_employee(request, branch_id):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        employee_info = data.get('employeeInfo', {})
        new_employee_obj = Employee.objects.create(
            first_name=employee_info.get('name'),
            last_name=employee_info.get('surname'),
            branch_id=branch_id,
            genre=employee_info.get('genre'),  # Assuming genre is a field in Employee
            role=employee_info.get('role'),
            skill_class=employee_info.get('class'),  # Assuming class is a field in Employee
            contract_type=employee_info.get('contract'),  # Assuming contract is a field in Employee
            contract_start=employee_info.get('contractStart'),
            contract_end=employee_info.get('contractEnd'),
            phone_number=employee_info.get('telNumber'),
            email=employee_info.get('email'),
            birth_date=employee_info.get('birthDate'),
            # Add other fields as necessary
        )
        new_employee_obj.save()

        all_employees = list(
            Employee.objects.filter(branch_id=branch_id).values('id', 'branch__name', 'first_name', 'last_name')
        )
        return JsonResponse({'status': 'success', 'employee_id': 2, 'all_employees': all_employees})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def update_employee(request, branch_id, employee_id):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        employee_info = data.get('employeeInfo', {})
        try:
            employee = Employee.objects.get(id=employee_id)
            employee.first_name = employee_info.get('name')
            employee.last_name = employee_info.get('surname')
            employee.branch_id = branch_id  # Assuming branch_id is passed in the request
            employee.genre = employee_info.get('genre')
            employee.role = employee_info.get('role')
            employee.skill_class = employee_info.get('class')
            employee.contract_type = employee_info.get('contract')
            employee.contract_start = employee_info.get('contractStart')
            employee.contract_end = employee_info.get('contractEnd')
            employee.phone_number = employee_info.get('telNumber')
            employee.email = employee_info.get('email')
            employee.birth_date = employee_info.get('birthDate')
            employee.max_hours_per_month = employee_info.get('monthlyHour')
            employee.hourly_cost = employee_info.get('hourlyCost')
            # Add other fields as necessary
            employee.save()

            return JsonResponse({'status': 'success', 'message': 'Employee updated successfully'})
        except Employee.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Employee not found'}, status=404)
    return None


def set_employee_rest_days(request, branch_id, employee_id):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        return JsonResponse({'status': 'success', 'message': 'Employee updated successfully'})