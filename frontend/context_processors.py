
from api.models import Branch

def get_branches(request):
    branches = Branch.objects.all()
    return {'branches': branches}