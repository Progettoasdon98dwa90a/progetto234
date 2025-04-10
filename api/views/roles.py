from django.http import JsonResponse

from api.models import Role


def get_all_roles(request):

    if request.method == 'GET':
        roles = Role.objects.all()

        data = {"data" : []}

        for role in roles:
            data['data'].append({
                'id': role.id,
                'name': role.name,
            })

        return JsonResponse(data)