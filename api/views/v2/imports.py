from datetime import datetime, timedelta

from django.http import JsonResponse
from django.shortcuts import render

from api.models import Branch, Import


def getHistory(request, year, branch_id):

    if request.method == 'GET':
        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Branch not found'})

        try:
            year = int(year)
            year = str(year)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid year'})

        imports_objs_qs = Import.objects.filter(branch=branch)
        imports_objs_qs_filtered = Import.objects.none()

        # Filter for all import_obj containing the requested year
        for import_obj in imports_objs_qs:
            if import_obj.import_date.__contains__(year):
                imports_objs_qs_filtered |= Import.objects.filter(import_date=import_obj.import_date)

        # Build dictionary of all days in the selected year
        start_date = datetime(int(year), 1, 1)
        end_date = datetime(int(year), 12, 31)
        all_days_in_year = [
            (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
            for i in range((end_date - start_date).days + 1)
        ]

        imports_report_mapped = {}

        # Mark days with import as 1
        for import_obj in imports_objs_qs_filtered:
            imports_report_mapped[import_obj.import_date] = 1
            if import_obj.import_date in all_days_in_year:
                all_days_in_year.remove(import_obj.import_date)

        # Remaining days get 0 for no import
        for day in all_days_in_year:
            imports_report_mapped[day] = 0

        # Now mark FUTURE days as -1
        today_str = datetime.now().strftime('%Y-%m-%d')
        today_date = datetime.strptime(today_str, '%Y-%m-%d').date()

        for day_str in imports_report_mapped.keys():
            day_date = datetime.strptime(day_str, '%Y-%m-%d').date()
            if day_date > today_date:
                imports_report_mapped[day_str] = -1

        # Sort dictionary by date
        imports_report_mapped = dict(sorted(imports_report_mapped.items()))

        context = {
            'imports': imports_report_mapped,
            'branch': branch.id,
            'year': year,
        }

        return JsonResponse(context)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})