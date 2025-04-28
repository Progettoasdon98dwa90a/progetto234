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

        target_sales = 200
        target_scontrini = 100
        target_ingressi = 100

        branch_sales_data = generate_branch_report_sales(branch_id, start_date_str, end_date_str)

        # 2. Prepare the data for the chart structure
        sales_values = list(branch_sales_data.values())
        sales_labels = list(branch_sales_data.keys())
        num_data_points = len(sales_labels)  # Or len(sales_values)

        # 3. Construct the final dictionary
        sales_chart_config = {
                "series": [
                    {
                        "name": "Incassi",
                        "data": sales_values
                    },
                    {
                        "name": "Totale sedi",  # Or perhaps "Target"? Adjust name if needed.
                        "data": [target_sales] * num_data_points
                    }
                ],
                "labels": sales_labels
        }

        report_data = {
            "sales": sales_chart_config,
            "receipts": [{'name': 'Scontrini',
                           'data': generate_branch_report_scontrini(branch_id, start_date_str, end_date_str)},
                          {'name': 'Totale sedi',
                           'data': [target_scontrini] * len(generate_branch_report_scontrini(branch_id, start_date_str, end_date_str))}
                          ],
            "entrances": generate_ingressi_branch_report(branch_id, start_date_str, end_date_str),
            "conversionRate": generate_branch_report_conversion_rate(branch_id, start_date_str, end_date_str),
        }

        return JsonResponse({"status": "success", "data": report_data})
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        # 0 = sales, 1 = 1 scontrini, 2 = ingressi + conversion_rate,
        chart_type = data.get("chart")
        # convert from DD-MM-YYYY to YYYY-MM-DD
        start_date_str = data.get("startDate")
        end_date_str = data.get("endDate")
        start_date_obj = datetime.strptime(start_date_str, "%d-%m-%Y").date()
        end_date_obj = datetime.strptime(end_date_str, "%d-%m-%Y").date()
        start_date_str = start_date_obj.strftime("%Y-%m-%d")
        end_date_str = end_date_obj.strftime("%Y-%m-%d")

        target_sales = 3000
        target_scontrini = 100
        target_ingressi = 100

        if chart_type == 0:
            # Sales
            obj = [{'name': 'Incassi',
              'data': generate_branch_report_sales(branch_id, start_date_str, end_date_str)},
             {'name': 'Totale sedi',
              'data': [target_sales] * len(generate_branch_report_sales(branch_id, start_date_str, end_date_str))}
             ]
            # Sales
            return JsonResponse(obj)
        elif chart_type == 1:
            # Scontrini
            obj = [
                {'name': 'Scontrini',
                 'data': generate_branch_report_scontrini(branch_id, start_date_str, end_date_str)},
                {'name': 'Totale sedi',
                 'data': [target_scontrini] * len(generate_branch_report_scontrini(branch_id, start_date_str, end_date_str))}
            ]
            return JsonResponse(obj)
        elif chart_type == 2:
            # Ingressi + Conversion Rate
            obj = [
                {'name': 'Ingressi',
                 'data': generate_branch_traffico_esterno_report(branch_id, start_date_str, end_date_str)},
                {'name': 'Tasso Conversione',
                 'data': generate_branch_report_conversion_rate(branch_id, start_date_str, end_date_str)}
            ]
            return JsonResponse(obj)
        else:
            return JsonResponse({"status": "error", "errors": ["Invalid chart type"]}, status=400)
    return JsonResponse({"status": "error", "errors": ["Invalid request method"]}, status=405)




