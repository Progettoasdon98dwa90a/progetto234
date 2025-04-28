import json

from django.http import JsonResponse
from datetime import datetime, timedelta

from django.views.decorators.csrf import csrf_exempt

from api.formulas.counter import generate_ingressi_branch_report, generate_branch_report_conversion_rate
from api.formulas.receipts import generate_branch_report_scontrini
from api.formulas.sales import generate_branch_report_sales
from api.models import Branch


@csrf_exempt
def get_branch_report(request, branch_id):
    target_sales = 200
    target_scontrini = 100
    target_ingressi = 100

    if request.method == 'GET':
        # Calculate fallback to the last 30 days
        start_date = datetime.now() - timedelta(days=371) # 7 days
        end_date = datetime.now() - timedelta(days=365)

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


        # Generate the sales chart data
        branch_sales_data = generate_branch_report_sales(branch_id, start_date_str, end_date_str)
        sales_values = list(branch_sales_data.values())
        sales_labels = list(branch_sales_data.keys())
        sales_num_data_points = len(sales_labels)  # Or len(sales_values)
        sales_chart_config = {
                "series": [
                    {
                        "name": "Incassi",
                        "data": sales_values
                    },
                    {
                        "name": "Totale sedi",  # Or perhaps "Target"? Adjust name if needed.
                        "data": [target_sales] * sales_num_data_points
                    }
                ],
                "labels": sales_labels
        }
        # Generate the receipts chart data
        receipts_data = generate_branch_report_scontrini(branch_id, start_date_str, end_date_str)
        receipts_values = list(receipts_data.values())
        receipts_labels = list(receipts_data.keys())
        receipts_chart_config = { #NO TOTALE SEDI
            "series": [
                {
                    "name": "Scontrini",
                    "data": receipts_values
                },
            ],
            "labels": receipts_labels
        }
        # Generate the entrances chart data
        entrances_data = generate_ingressi_branch_report(branch_id, start_date_str, end_date_str)
        entrances_values = list(entrances_data.values())
        entrances_labels = list(entrances_data.keys())
        conversion_rate_date = generate_branch_report_conversion_rate(branch_id, start_date_str, end_date_str)
        conversion_rate_values = list(conversion_rate_date.values())
        entrances_chart_config = {  # NO TOTALE SEDI
            "series": [
                {
                    "name": "Ingressi",
                    "data": entrances_values
                },
                {
                    "name": "Tasso di Conversione",
                    "data": conversion_rate_values
                },
            ],
            "labels": entrances_labels
        }

        report_data = {
            "sales": sales_chart_config,
            "receipts": receipts_chart_config,
            "entrances": entrances_chart_config,
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

        if chart_type == 0:
            # Generate the sales chart data
            branch_sales_data = generate_branch_report_sales(branch_id, start_date_str, end_date_str)
            sales_values = list(branch_sales_data.values())
            sales_labels = list(branch_sales_data.keys())
            sales_num_data_points = len(sales_labels)  # Or len(sales_values)
            sales_chart_config = {
                "series": [
                    {
                        "name": "Incassi",
                        "data": sales_values
                    },
                    {
                        "name": "Totale sedi",  # Or perhaps "Target"? Adjust name if needed.
                        "data": [target_scontrini] * sales_num_data_points
                    }
                ],
                "labels": sales_labels
            }
            return JsonResponse(sales_chart_config)
        elif chart_type == 1:
            receipts_data = generate_branch_report_scontrini(branch_id, start_date_str, end_date_str)
            receipts_values = list(receipts_data.values())
            receipts_labels = list(receipts_data.keys())
            receipts_chart_config = {  # NO TOTALE SEDI
                "series": [
                    {
                        "name": "Scontrini",
                        "data": receipts_values
                    },
                ],
                "labels": receipts_labels
            }
            return JsonResponse(receipts_chart_config)
        elif chart_type == 2:
            entrances_data = generate_ingressi_branch_report(branch_id, start_date_str, end_date_str)
            entrances_values = list(entrances_data.values())
            entrances_labels = list(entrances_data.keys())
            conversion_rate_date = generate_branch_report_conversion_rate(branch_id, start_date_str, end_date_str)
            conversion_rate_values = list(conversion_rate_date.values())
            entrances_chart_config = {  # NO TOTALE SEDI
                "series": [
                    {
                        "name": "Ingressi",
                        "data": entrances_values
                    },
                    {
                        "name": "Tasso di Conversione",
                        "data": conversion_rate_values
                    },
                ],
                "labels": entrances_labels
            }
            return JsonResponse(entrances_chart_config)
        else:
            return JsonResponse({"status": "error", "errors": ["Invalid chart type"]}, status=400)
    return JsonResponse({"status": "error", "errors": ["Invalid request method"]}, status=405)


def get_branch_employees_report(request, branch_id):
    if request.method == 'GET':
        # fallback to start of the year until now
        start_date_str = datetime.now().strftime("%Y-%m-%d")
        end_date_str = datetime.now().strftime("%Y-%m-%d")
        try:
            branch_id = int(branch_id)
        except ValueError:
            return JsonResponse({"status": "error", "errors": ["Invalid branch ID"]}, status=400)
        employees_chart_config = {  # NO TOTALE SEDI
            "series": [
                {
                    "name": "Ingressi",
                    "data": entrances_values
                },
                {
                    "name": "Tasso di Conversione",
                    "data": conversion_rate_values
                },
            ],
            "labels": entrances_labels
        }

        main_obj = {
            'employees' : {
                'series': [
                    {
                        'name': 'Media Pezzi Venduti',
                        'data' : [300, 300, 300, 300, 300, 300]
                    },
                    {
                        'name': 'Scontrino Medio',
                        'data': [50.3, 50.3, 50.3, 50.3, 50.3, 50.3]
                    },
                    {
                        'name': 'Media Numero Scontrini',
                        'data': [150, 150, 150, 150, 150, 150]
                    }
                ],
            'labels': ["Gianni", "Giorgio", "Giovanni", "Giulio", "Giuseppe", "Giovanni"]
            }
        }

        return JsonResponse({"status": "success", "data": main_obj})

    return None