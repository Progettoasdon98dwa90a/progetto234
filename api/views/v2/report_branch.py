import json
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt

from api.formulas.averages import generate_medium_performance
from api.formulas.counter import generate_ingressi_branch_report, generate_branch_report_conversion_rate
from api.formulas.receipts import generate_branch_report_scontrini, generate_report_performance_scontrini
from api.formulas.sales import generate_branch_report_sales, generate_report_performance_sales, \
    generate_number_sales_performance
from api.models import Branch, Employee


# Constants
TARGETS = {'sales': 200, 'scontrini': 100, 'ingressi': 100}
CHART_TYPES = {'SALES': 0, 'RECEIPTS': 1, 'ENTRANCES': 2}


def parse_date(date_str, format_from, format_to='%Y-%m-%d'):
    """Parse and convert date between formats"""
    return datetime.strptime(date_str, format_from).strftime(format_to)


def get_dates(request, default_days=7):
    """Get and validate date range from request"""
    try:
        if request.method == 'GET':
            start_date = datetime.now() - timedelta(days=default_days + 1)
            end_date = datetime.now() - timedelta(days=1)
            return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

        data = json.loads(request.body.decode('utf-8'))
        start_str = parse_date(data['startDate'], '%d-%m-%Y')
        end_str = parse_date(data['endDate'], '%d-%m-%Y')
        return start_str, end_str

    except (KeyError, json.JSONDecodeError):
        return JsonResponse(
            {"status": "error", "errors": ["Invalid date format"]},
            status=400
        )


def get_branch(branch_id):
    """Validate and return branch object"""
    try:
        return Branch.objects.get(id=int(branch_id))
    except (ValueError, Branch.DoesNotExist):
        return None


def build_chart_config(data, chart_type, target=None):
    """Build standardized chart configuration"""
    config = {
        "series": [{"name": chart_type, "data": list(data.values())}],
        "labels": list(data.keys())
    }

    if target:
        config["series"].append({
            "name": "Target",
            "data": [target] * len(data)
        })

    return config


@csrf_exempt
def get_branch_report(request, branch_id):
    """Handle branch report requests"""
    branch = get_branch(branch_id)
    if not branch:
        return JsonResponse(
            {"status": "error", "errors": ["Invalid branch ID"]},
            status=400
        )

    if request.method == 'GET':
        start_date, end_date = get_dates(request, 7)
        report_data = {
            "sales": build_chart_config(
                generate_branch_report_sales(branch.id, start_date, end_date),
                "Incassi",
                TARGETS['sales']
            ),
            "receipts": build_chart_config(
                generate_branch_report_scontrini(branch.id, start_date, end_date),
                "Scontrini"
            ),
            "entrances": {
                "series": [
                    {"name": "Ingressi", "data": list(generate_ingressi_branch_report(branch.id, start_date, end_date).values())
                     },
                    {"name": "Tasso di Conversione", "data": list(
                        generate_branch_report_conversion_rate(
                            branch.id, start_date, end_date).values())
                     }
                ],
                "labels": list(generate_ingressi_branch_report(
                    branch.id, start_date, end_date).keys())
            }
        }
        return JsonResponse({"status": "success", "data": report_data})

    if request.method == 'POST':
        try:
            chart_type = json.loads(request.body.decode('utf-8')).get("chart")
            start_date, end_date = get_dates(request)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "errors": ["Invalid request body"]},
                status=400
            )

        generators = {
            CHART_TYPES['SALES']: (generate_branch_report_sales, "Incassi", TARGETS['sales']),
            CHART_TYPES['RECEIPTS']: (generate_branch_report_scontrini, "Scontrini", None),
            CHART_TYPES['ENTRANCES']: (generate_ingressi_branch_report, "Ingressi", None)
        }

        if chart_type not in generators:
            return JsonResponse(
                {"status": "error", "errors": ["Invalid chart type"]},
                status=400
            )

        generator, name, target = generators[chart_type]
        data = generator(branch.id, start_date, end_date)

        if chart_type == CHART_TYPES['ENTRANCES']:
            conversion_data = generate_branch_report_conversion_rate(
                branch.id, start_date, end_date)
            config = {
                "series": [
                    {"name": name, "data": list(data.values())},
                    {"name": "Tasso di Conversione", "data": list(conversion_data.values())}
                ],
                "labels": list(data.keys())
            }
        else:
            config = build_chart_config(data, name, target)

        return JsonResponse(config)

    return JsonResponse(
        {"status": "error", "errors": ["Invalid request method"]},
        status=405
    )


@csrf_exempt
def get_branch_employees_report(request, branch_id):
    """Handle employee performance reports"""
    branch = get_branch(branch_id)
    if not branch:
        return JsonResponse(
            {"status": "error", "errors": ["Invalid branch ID"]},
            status=400
        )

    employees = Employee.objects.filter(branch_id=branch.id)
    if not employees.exists():
        return JsonResponse(
            {"status": "error", "errors": ["No employees found"]},
            status=400
        )

    try:
        start_date, end_date = get_dates(request)
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "error", "errors": ["Invalid date format"]},
            status=400
        )

    # Generate report data
    report_data = {
        'sales': generate_report_performance_sales(branch.id, start_date, end_date),
        'scontrini': generate_report_performance_scontrini(branch.id, start_date, end_date),
        'num_sales': generate_number_sales_performance(branch.id, start_date, end_date)
    }

    # Process averages
    averages = {
        'medium_sales': generate_medium_performance(report_data['sales']),
        'medium_scontrini': generate_medium_performance(report_data['scontrini']),
        'medium_num_sales': generate_medium_performance(report_data['num_sales'])
    }

    # Build response structure
    response_data = {
        'employees': {
            'series': [
                {'name': 'Media Pezzi Venduti', 'data': list(averages['medium_num_sales'].values())},
                {'name': 'Scontrino Medio', 'data': list(averages['medium_sales'].values())},
                {'name': 'Media Numero Scontrini', 'data': list(averages['medium_scontrini'].values())}
            ],
            'labels': [emp.get_full_name() for emp in employees]
        },
        'mediumNumberSales': {
            'series': [{
                'name': emp,
                'data': values
            } for emp, values in report_data['num_sales'].items()],
            'labels': [(datetime.strptime(start_date, "%Y-%m-%d") + timedelta(n)).strftime("%Y-%m-%d")
                       for n in range((datetime.strptime(end_date, "%Y-%m-%d") -
                                       datetime.strptime(start_date, "%Y-%m-%d")).days + 1)]
        }
    }

    return JsonResponse({"status": "success", "data": response_data})