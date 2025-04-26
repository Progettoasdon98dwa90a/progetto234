import json

from django.http import JsonResponse
from datetime import datetime, timedelta

from django.views.decorators.csrf import csrf_exempt

from api.formulas.counter import generate_ingressi_branch_report, generate_branch_report_conversion_rate, \
    generate_branch_traffico_esterno_report
from api.formulas.receipts import generate_branch_report_scontrini
from api.formulas.sales import generate_branch_report_sales
from api.models import Branch
from api.formulas.counter import generate_branch_tasso_attrazione_report


@csrf_exempt
def get_branch_report(request, branch_id):
    if request.method == 'GET':
        # Calculate fallback to the last 30 days
        start_date = datetime.now() - timedelta(days=371) # 7 days
        end_date = datetime.now()  - timedelta(days=365)

        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        try:
            branch_id = int(branch_id)
        except ValueError:
            return JsonResponse({"status": "error", "errors": ["Invalid branch ID"]}, status=400)

        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return JsonResponse({"status": "error", "errors": ["Branch not found"]}, status=400)

        report_data = {
            "sales": generate_branch_report_sales(branch_id, start_date_str, end_date_str),
            "receipts": generate_branch_report_scontrini(branch_id, start_date_str, end_date_str),
            "entrances": generate_ingressi_branch_report(branch_id, start_date_str, end_date_str),
            "conversionRate": generate_branch_report_conversion_rate(branch_id, start_date_str, end_date_str),
        }

        return JsonResponse({"status": "success", "data": report_data})
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        # 0 = sales, 1 = 1 scontrini, 2 = ingressi + conversion_rate,
        chart_type = data.get("chart")

        if chart_type == 0:
            start_date_str = data.get("startDate")
            end_date_str = data.get("endDate")
            # Sales
            return JsonResponse(generate_branch_report_sales(branch_id, start_date_str, end_date_str))
        elif chart_type == 1:
            start_date_str = data.get("startDate")
            end_date_str = data.get("endDate")
            # Scontrini
            return JsonResponse(generate_branch_report_scontrini(branch_id, start_date_str, end_date_str))
        elif chart_type == 2:
            start_date_str = data.get("startDate")
            end_date_str = data.get("endDate")
            # Ingressi + Conversion Rate
            ingressi = generate_ingressi_branch_report(branch_id, start_date_str, end_date_str)
            conversion_rate = generate_branch_report_conversion_rate(branch_id, start_date_str, end_date_str)
            return JsonResponse({"ingressi": ingressi, "conversion_rate": conversion_rate})
        else:
            return JsonResponse({"status": "error", "errors": ["Invalid chart type"]}, status=400)
    return JsonResponse({"status": "error", "errors": ["Invalid request method"]}, status=405)




