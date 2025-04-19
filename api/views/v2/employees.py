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
        "dipendenteInfo": {
            "nome": employee.first_name,
            "cognome": employee.last_name,
            "genere": employee.format_gender(),  # Enum numerico (es. 0=Non specificato, 1=Maschio, 2=Femmina)
            "dataNascita": "DEFINIRE FORMATO E TIMEZONE",
            "telefono": "AGGIUNGERE",
            "email": "AGGIUNGERE"
        },
        "contrattoDipendente": {
            "ruolo": "",
            "classe": "",
            "sede": branch_id,  # ID numerico della sede
            "contratto": "",  # Valori possibili da TipoContratto (non specificato nell'originale)
            "oreMensili": employee.role.max_hours_per_month,
            "costoOrario": "",
            "inizioContratto": None,
            "fineContratto": None
        },
        "giornoDIRiposo": "",  # Valori possibili: "Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"
        "ferie": [],  # Array di oggetti Ferie (struttura non specificata nell'originale)
        "oreLavorate": {
            "oreLavorate": "",
            "oreTotal": ""
        }, # capire se fare fallback su ultimi 30 gg
        "vendite": {
            "scontrinoMedio": get_scontrini_dipendente_date_range(employee_id, start_date_str, end_date_str),  # Oggetto Metrica non definito nell'originale
            "mediaScontrini": {},
            "mediaPrezziScontrini": {},
            "dataInizio": None,
            "dataFine": None
        }
    }

    return JsonResponse(dipendente_schema)

@csrf_exempt
def new_employee(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))

        print(data)

        return JsonResponse({'status': 'success', 'employee_id': new_employee.id})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)