from django.http import JsonResponse

from api.models import Branch, Employee


def get_all_branches(request):

    if request.method == 'GET':
        branches = Branch.objects.all()

        data = {"data" : []}

        for branch in branches:
            data['data'].append({
                'id': branch.id,
                'name': branch.name,
            })

        return JsonResponse(data)


def get_branch_employees(request, branch_id):

    if request.method == 'GET':
        try:
            branch = Branch.objects.get(id=branch_id)
            employees = Employee.objects.filter(branch=branch)

            data = {"data" : []}

            for employee in employees:
                data['data'].append({
                    'id': employee.id,
                    'name': f"({employee.id}) {employee.first_name} {employee.last_name}",
                })

            return JsonResponse(data)
        except Branch.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Branch not found'})