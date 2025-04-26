from django.http import JsonResponse
from datetime import datetime, timedelta

from api.formulas.counter import generate_ingressi_branch_report, generate_branch_report_conversion_rate, \
    generate_branch_traffico_esterno_report
from api.formulas.receipts import generate_branch_report_scontrini
from api.formulas.sales import generate_branch_report_sales
from api.models import Branch
from api.formulas.counter import generate_branch_tasso_attrazione_report


def get_branch_report(request, branch_id):
    # Calculate fallback to the last 30 days
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()

    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    start_date_str = '2024-01-01'
    end_date_str = '2024-01-31'

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
        "scontrini": generate_branch_report_scontrini(branch_id, start_date_str, end_date_str),
        "ingressi": generate_ingressi_branch_report(branch_id, start_date_str, end_date_str),
        "tasso_attrazione": generate_branch_tasso_attrazione_report(branch_id, start_date_str, end_date_str),
        "conversion_rate": generate_branch_report_conversion_rate(branch_id, start_date_str, end_date_str),
        "traffico_esterno": generate_branch_traffico_esterno_report(branch_id, start_date_str, end_date_str),
    }

    return JsonResponse({"status": "success", "data": report_data})
