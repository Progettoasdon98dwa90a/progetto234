import calendar
import datetime
import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.models import Branch, Target

logger = logging.getLogger(__name__)

def target_grid(request):
    if request.method == 'GET':
        # first of current month to last of current month
        now = datetime.datetime.now()

        first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).date()
        _, num_days = calendar.monthrange(now.year, now.month)

        last_day = now.replace(day=num_days, hour=23, minute=59, second=59, microsecond=999999).date()
        all_branches = Branch.objects.all()
        all_monthly_targets = Target.objects.filter(start_date=first_day, end_date=last_day)

        grid_data = []

        # sum all sales_target from all_monthly targets
        GLOBAL_TARGET = sum(target.sales_target for target in all_monthly_targets)
        # create a GLOBAL target ROW
        row_data = {
            'id': 'Globale',
            'branch': 'Globale',  # Corresponds to 'Sede'
            'weeklyTarget': GLOBAL_TARGET / 4,  # Calculated value or None/0
            'monthlyTarget': GLOBAL_TARGET,  # Target value or None/0
            'lastUpdate': 15000,  # Formatted date/time string or None
        }
        grid_data.append(row_data)

        for branch in all_branches:
            # Find the target for the current branch and month, default to None if not found
            target = all_monthly_targets.filter(branch=branch).first()
            # Prepare values, handling cases where a target might not exist or sales_target is null

            last_update_val = 1500.00 # mocked for now

            # Create the dictionary for this row
            row_data = {
                'id': branch.id,
                'branch': branch.name,  # Corresponds to 'Sede'
                'weeklyTarget': target.sales_target / 4,  # Calculated value or None/0
                'monthlyTarget': target.sales_target,  # Target value or None/0
                'lastUpdate': last_update_val,  # Formatted date/time string or None
            }
            grid_data.append(row_data)

        return JsonResponse({'status': 'success', 'data': grid_data}, status=200)
    elif request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
            branch_id = body.get('branchId')
            new_target = body.get('targetValue')

            target = Target.objects.get(branch_id=branch_id)
            target.sales_target = new_target
            target.save()

            return JsonResponse({'status': 'success', 'message': 'Target updated successfully'}, status=200)
        except Target.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Target not found'}, status=404)
        except Exception as e:
            logger.error(f"Error updating target: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Failed to update target'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
