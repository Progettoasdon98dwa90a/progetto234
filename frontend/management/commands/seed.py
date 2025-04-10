from datetime import datetime
from pathlib import Path
from django.core.management import BaseCommand
from django.http import JsonResponse
from openpyxl import load_workbook
from django.core.management import call_command


from api.models import Employee, Role, Branch, Import

current_directory = Path(__file__).resolve().parent.parent.parent.parent

print(current_directory)



class Command(BaseCommand):
    help = "Assigns all weapons to users, without duplicates, until finished"

    def handle(self, *args, **options):
        # create first two branches
        call_command('flush', interactive=False)  # Flush the database
        

        branch_data = [
                {'name': 'Biella', 'extra_data': {'brand' : 'equivalenza'}},
                {'name': 'OM-Siderno', 'extra_data': {'brand' : 'original'}},
            ]

        for branch in branch_data:
            Branch.objects.create(**branch)
            print(f"Branch '{branch['name']}' created successfully.")
        
            # Specify the path to the local file
        import_data_file = current_directory / 'utils_files' / 'Dati-Biella-2024.xlsx'

        # Load the workbook from the local file
        workbook = load_workbook(filename=import_data_file)

        # Access the sheet
        sheet = workbook.active  # You can specify sheet name if needed

        # Initialize the dictionary to hold the data
        data_dict = {}

        # Iterate through the rows, skipping the header
        for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip the header row
            date = row[1]  # assuming the date is in the second column
            record = {
                "Dipendente": row[0],
                "Qta. Vend.": row[2],
                "Sco.": row[3],
                "Importo": row[4],
                "Sco. Medio": row[5],
                "Qta Media": row[6]
            }

            # If the date is already a key, append the new record to its list
            if date in data_dict:
                data_dict[date].append(record)
            else:
                # Otherwise, create a new list with the record
                data_dict[date] = [record]

        import_qs = Import.objects.none()

        errors = []
        selected_branch = 1
        selected_type = 'sales_data'
        branch_obj = Branch.objects.get(id=selected_branch)
        roles_data = {
                'Operatore': {
                    'max_hours_per_day': 8,
                    'max_services_per_week': 5,
                    'max_hours_per_week': 40,
                    'max_hours_per_month': 160,
                },
            }

        for role, role_data in roles_data.items():
            role_obj = Role.objects.create(**role_data)

            print(f"Role '{role}' created successfully.")

        employees_data = [{
                    'id': 1,
                    'first_name': 'Elisa',
                    'last_name': "1",
                    'branch': branch_obj,
                    'role': Role.objects.get(id=1),  # Assuming you have a Role model
                    
                },
                {
                    'id': 2,
                    'first_name': 'Vanessa',
                    'last_name': "1",
                    'branch': branch_obj,
                    'role': Role.objects.get(id=1),  # Assuming you have a Role model
                    
                },
                {
                    'id': 3,
                    'first_name': 'Vanessa',
                    'last_name': "Brocca",
                    'branch': branch_obj,
                    'role': Role.objects.get(id=1),  # Assuming you have a Role model
                    
                },
                {
                    'id': 4,
                    'first_name': 'Venditore',
                    'last_name': "Christmas",
                    'branch': branch_obj,
                    'role': Role.objects.get(id=1),  # Assuming you have a Role model
                    
                },

            ]
        
        for employee in employees_data:
            employee_obj = Employee.objects.create(**employee)
            print(f"Employee '{employee['first_name']}' created successfully.")


        for date, records in data_dict.items():
            employees_day_id_list = []
            date = datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')
            for record in records:
                try:
                    employees_day_id_list.append(record['Dipendente'])
                except:
                    errors.append(f"Employee {record['Dipendente']} not found")
                    continue

            employees_day_qs = Employee.objects.filter(id__in=employees_day_id_list)

            if employees_day_qs.count() != len(employees_day_id_list):
                errors.append(f"Employees on {date} not found")
                continue

            branch_check_value = list(employees_day_qs.values_list('branch', flat=True))
            normalized = list(dict.fromkeys(branch_check_value))
            if len(normalized) != 1:
                errors.append(f"Branch on {date} from different branch")
                continue

            if normalized[0] != selected_branch:
                errors.append(f"Branch on {date} from different branch")
                continue

            if Import.objects.filter(branch=branch_obj, import_date=date):
                errors.append(f"Collision on {date}")
                continue

        if errors:
            return JsonResponse({"status": "error", "errors": errors}, status=200)

        import_bulk_create_list = []
        for date, data in data_dict.items():
            date_obj = datetime.strptime(date, '%d/%m/%Y')
            date_str = date_obj.strftime('%Y-%m-%d')
            i = Import(import_date=date_str, data=data, branch=branch_obj, import_type=selected_type)
            import_bulk_create_list.append(i)

        Import.objects.bulk_create(import_bulk_create_list)
        print("Import data created successfully.")