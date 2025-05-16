from django.http import JsonResponse
from django.shortcuts import render

from api.formulas.averages import generate_medium_performance, generate_medium_sales
from api.formulas.receipts import generate_report_performance_scontrini
from api.formulas.sales import generate_report_performance_sales
from api.models import Branch

def get_employees_report(request, branch_id):
    if request.method == 'GET':
        # Get the query string parameters
        date_param = request.GET.get('date')
        date_param = "2024-01-01 to 2025-01-31"

        # Validate branch parameter
        if not branch_id:
            return JsonResponse({"status": "error", "errors": ["No branch selected"]}, status=400)
        try:
            branch_id = int(branch_id)
        except ValueError:
            return JsonResponse({"status": "error", "errors": ["Invalid branch ID"]}, status=400)

        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return JsonResponse({"status": "error", "errors": ["Branch not found"]}, status=400)

        if branch.get_brand() == "original":
            return JsonResponse({"status": "error", "errors": ["Original Marines No Employees Performances"]}, status=400)

        # Convert the date parameter to string (it may be None)
        date = str(date_param) if date_param else ""

        # Initialize date_start and date_end
        date_start, date_end = None, None

        # Check if the date string contains a range (using "to")
        if "to" in date:
            parts = date.split("to")
            if len(parts) >= 2:
                date_start = parts[0].strip()
                date_end = parts[1].strip()
            else:
                date_start = date.strip()
                date_end = date.strip()
        else:
            # If no range is provided, you could either treat it as a single date or return an error.
            # Here, we treat it as a single date.
            date_start = date.strip()
            date_end = date.strip()

        # Generate the report (adjust parameters as needed)



        sc_performance = generate_report_performance_scontrini(branch_id, date_start, date_end)

        sales_performance = generate_report_performance_sales(branch_id, date_start, date_end)


        medium_sc_sales = generate_medium_performance(sc_performance) # Use the generic average function

        medium_sales_performance = generate_medium_performance(sales_performance)

        medium_number_sales_performance = generate_medium_sales(sales_performance)

        zoom_enabled = "true"
        graph_type = "area"

        if date_start == date_end:
            zoom_enabled = "false"
            graph_type = "bar"

        total_sales = sum([sum(sales) for sales in sales_performance.values()])
        total_sc = sum([sum(sc) for sc in sc_performance.values()])

        # Calculate the percentage for each employee within each KPI
        sales_percentage = {key: round((sum(sales) / total_sales) * 100, 2) if total_sales != 0 else 0
                            for key, sales in sales_performance.items()}
        sc_percentage = {key: round((sum(sc) / total_sc) * 100, 2) if total_sc != 0 else 0
                         for key, sc in sc_performance.items()}


        context = {
            "sc_performance": sc_performance,
            "branch": branch_id,
            "date_start": date_start,
            "date_end": date_end,
            "sales_performance": sales_performance,
            "sales_percentage": sales_percentage,
            "sc_percentage": sc_percentage,
            "zoom_enabled": zoom_enabled,
            "type" : graph_type,
        }

        return JsonResponse(context, status=200)