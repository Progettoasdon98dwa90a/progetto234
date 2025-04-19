# formulas/schedule.py
"""
Functions related to employee schedules and calculating worked hours.
"""
import json
from datetime import datetime # Keep if needed for date parsing, maybe not here

from api.models import Employee, Schedule, Branch # Import Branch too

# orario_exists: Checks if a schedule exactly matching the given start and end dates exists.
# Output: boolean (True if exists, False otherwise)
def orario_exists(start_date, end_date):
    # ... (copy function code from original file) ...
    return Schedule.objects.filter(start_date=start_date, end_date=end_date).exists()


# get_employee_worked_hours_single_day: Calculates total hours worked by an employee on a specific day based on schedule data (assuming 30min slots).
# Input: date should be a string "YYYY-MM-DD"
# Output: float (hours worked), 0.0 (not scheduled/no data), or -1.0 (no schedule object covering the date or error).
def get_employee_worked_hours_single_day(employee_id, date):
    # ... (copy function code from original file) ...
    employee = None

    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        print(f"HOURS: Employee with ID {employee_id} does not exist.")
        return -1.0 # Indicate employee not found

    branch = employee.branch
    if not branch:
        print(f"HOURS: Employee {employee_id} is not associated with a branch.")
        return -1.0 # Indicate missing branch association

    try:
        # Find schedule covering the date for the employee's branch
        schedule_obj = Schedule.objects.get(start_date__lte=date, end_date__gte=date, branch=branch)
    except Schedule.DoesNotExist:
        # This is common - no schedule defined for this period/branch
        # print(f"HOURS Info: No schedule found covering date {date} for branch {branch.id}")
        return -1.0 # Indicate no schedule object found
    except Schedule.MultipleObjectsReturned:
         # This indicates overlapping schedules for the same branch, which might be an issue
         print(f"HOURS Error: Multiple schedules found covering date {date} for branch {branch.id}. Using the first one found.")
         schedule_obj = Schedule.objects.filter(start_date__lte=date, end_date__gte=date, branch=branch).first()
         if not schedule_obj: return -1.0 # Should not happen based on exception

    # Parse schedule_data if it is a JSON string, handle potential errors
    schedule_data = schedule_obj.schedule_data
    parsed_schedule_data = None
    if isinstance(schedule_data, str):
        try:
            parsed_schedule_data = json.loads(schedule_data)
        except json.JSONDecodeError:
            print(f"HOURS Error: Decoding schedule JSON failed for schedule ID {schedule_obj.id}")
            return -1.0 # Indicate schedule data error
    elif isinstance(schedule_data, dict):
        parsed_schedule_data = schedule_data # Already a dict
    else:
         print(f"HOURS Error: Schedule data for schedule ID {schedule_obj.id} is not a dictionary or JSON string.")
         return -1.0 # Indicate schedule data format error

    if not parsed_schedule_data:
         print(f"HOURS Error: Failed to load schedule data for schedule ID {schedule_obj.id}")
         return -1.0

    # Get the schedule for the specific date string key
    day_schedule = parsed_schedule_data.get(date) # Use .get() for safe access
    if not day_schedule or not isinstance(day_schedule, dict):
        # This is common - the schedule exists but has no entry for this specific day
        # print(f"HOURS Info: No schedule data found for date {date} within schedule ID {schedule_obj.id}")
        return 0.0 # Return 0 hours if no data for this specific day

    worked_slots = 0
    employee_id_str = str(employee_id) # Convert employee ID to string for comparison

    # Loop over each time block in the day's schedule
    for time_key, employee_list in day_schedule.items():
        # Ensure employee_list is actually a list of IDs (can be strings or ints)
        if isinstance(employee_list, list):
            # Check if the employee ID (as string) is in the list of employee IDs (compare as strings)
            if employee_id_str in [str(emp) for emp in employee_list]:
                worked_slots += 1
        else:
            # Log warning about unexpected format? e.g., not a list for a time slot
            # print(f"HOURS Warning: Unexpected data format for time slot '{time_key}' on {date} in schedule {schedule_obj.id}. Expected list, got {type(employee_list)}")
            pass

    # Each slot represents 30 minutes (0.5 hours)
    worked_hours = worked_slots * 0.5
    return worked_hours