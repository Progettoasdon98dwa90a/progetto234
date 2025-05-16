from api.models import Import, Branch, Employee


def get_total_working_days_dipendente(employee_id):
    # get all the import 'sales_data' type from employee respective branch
    try:
        employee = Employee.objects.get(id=employee_id)
        branch = employee.branch
    except Employee.DoesNotExist:
        print(f"No employee found with ID {employee_id}")
        return None
    except Branch.DoesNotExist:
        print(f"No branch found for employee with ID {employee_id}")
        return None

    import_objs = Import.objects.filter(branch=branch, import_type="sales_data")
    total_working_days = 0

    for import_obj in import_objs:
        data = import_obj.data
        for employee_data in data:
            if employee_data['Dipendente'] == employee_id:
                total_working_days += 1
                continue

    return total_working_days

