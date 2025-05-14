import random
from datetime import timedelta, datetime

from procrastinate.contrib.django import app
import logging

from api.models import Schedule

logger = logging.getLogger('procrastinate')

@app.task()
def create_schedule(schedule_id):
    try:
        from orario_creation.main import fill_data_and_create_schedule
        logging.info("Creating schedule...")

        try:
            schedule_obj = Schedule.objects.get(id=schedule_id)
        except Schedule.DoesNotExist:
            logging.error(f"Schedule with ID {schedule_id} does not exist.")
            return

        if schedule_obj.processed:
            logging.error(f"Schedule with ID {schedule_id} has already been processed.")
            return

        result = fill_data_and_create_schedule(schedule_obj=schedule_obj)
        logging.info("Schedule created...")
        logging.info("Converting schedule data to events...")
        convert_schedule_data_to_events(result, schedule_obj)

        logging.info(f"Result: {str(result)[:50]}")
        return 0
    except Exception as e:
        logging.error(f"Error creating schedule: {e}")
        return 1

import logging
from datetime import datetime, timedelta

# Assuming api.models.ScheduleEvent and api.models.Employee are defined elsewhere
# from api.models import ScheduleEvent, Employee

def convert_schedule_data_to_events(schedule_data, schedule_obj):
    """
    Converts structured schedule data (list of assignments per day)
    into ScheduleEvent objects.

    Args:
        schedule_data (dict): A dictionary where keys are date strings
                              (e.g., "YYYY-MM-DD") and values are lists
                              of assignment dictionaries.
                              Example: {"2023-10-27": [{"service_name": "M", "employees": ["emp1_id"]}, {"service_name": "M", "employees": ["emp2_id"]}]}
        schedule_obj: The Schedule object containing shift definitions in its
                      'shift_data' attribute.
                      Example: schedule_obj.shift_data = [{"name": "M", "start": "9:00", "end": "13:00"}, ...]
    """
    from api.models import ScheduleEvent, Employee # Import models inside if needed

    shifts_data = schedule_obj.shift_data
    events_to_create = [] # Collect events to create in bulk

    if not isinstance(shifts_data, list):
        logging.error("schedule_obj.shift_data is not a list.")
        return # Or raise an error

    # Iterate through each day in the schedule data
    for day_str, assignments_list in schedule_data.items():

        # Ensure the value for the day key is a list as expected
        if not isinstance(assignments_list, list):
            # This handles cases where a day might have a different, unexpected format
            logging.warning(f"Skipping invalid entry for day {day_str}: Expected a list, but got {type(assignments_list)}. Data: {assignments_list}")
            continue

        # Iterate through each assignment entry within the day's list
        for assignment_data in assignments_list:

            # Ensure each assignment entry is a dictionary
            if not isinstance(assignment_data, dict):
                 logging.warning(f"Skipping invalid assignment entry for day {day_str}: Expected a dictionary, but got {type(assignment_data)}. Data: {assignment_data}")
                 continue

            service_name = assignment_data.get('service_name')
            # Assuming 'employees' is the key and its value is a list of employee identifiers
            assigned_employee_ids = assignment_data.get('employees', [])

            if not service_name:
                logging.warning(f"Skipping assignment entry for day {day_str}: 'service_name' missing or empty in {assignment_data}.")
                continue

            # 1. Find the corresponding shift definition from shifts_data
            selected_shift = None
            try:
                for shift in shifts_data:
                    if shift.get('name') == service_name:
                        selected_shift = shift
                        break # Found the shift, no need to check others
            except Exception as e:
                 logging.error(f"Error searching for shift '{service_name}' for assignment on day {day_str}: {e}")
                 continue # Skip this specific assignment entry

            if not selected_shift:
                logging.warning(f"No shift definition found for service name '{service_name}' in schedule_obj.shift_data for assignment on day {day_str}. Skipping.")
                continue # Skip this specific assignment entry

            # 2. Parse date and time strings into datetime objects
            start_time_str = selected_shift.get('start') # e.g., "9:00"
            end_time_str = selected_shift.get('end')   # e.g., "13:00"

            if not start_time_str or not end_time_str:
                logging.warning(f"Shift definition for '{service_name}' is missing start/end time for assignment on day {day_str}. Skipping.")
                continue

            try:
                # Construct full datetime strings by combining date from day_str and time from shift_data
                date_format = "%Y-%m-%d" # Adjust if your date format is different
                time_format = "%H:%M"   # Adjust if your time format is different
                full_datetime_format = f"{date_format} {time_format}"

                start_dt_str = f"{day_str} {start_time_str}"
                end_dt_str = f"{day_str} {end_time_str}"

                start_datetime = datetime.strptime(start_dt_str, full_datetime_format)
                end_datetime = datetime.strptime(end_dt_str, full_datetime_format)

                # Handle shifts that cross midnight (end time is on the next day)
                if end_datetime < start_datetime:
                    end_datetime += timedelta(days=1)
                    # No need to log this every time, maybe info level if desired
                    # logging.info(f"Adjusted end time to next day for assignment '{service_name}' on {day_str}.")

            except ValueError as e:
                logging.error(f"Error parsing date/time strings for assignment on day {day_str}, shift {service_name}: {e}")
                continue # Skip if date/time parsing fails
            except Exception as e: # Catch any other unexpected errors during parsing
                logging.error(f"Unexpected error processing date/time for assignment on day {day_str}, shift {service_name}: {e}")
                continue

            # 3. Process assigned employees and create events
            if not isinstance(assigned_employee_ids, list) or not assigned_employee_ids:
                # This assignment entry might be a shift without any employee listed
                logging.info(f"No employees listed in assignment {assignment_data} for day {day_str}, shift '{service_name}'. Skipping event creation for this entry.")
                continue # Skip this assignment entry if no employees or not a list

            # Fetch the Employee objects efficiently if assigned_employee_ids are PKs
            # Filter out any None or invalid IDs before querying
            # Also ensure IDs are strings if your PKs are strings, or convert if needed
            valid_employee_ids = [pk for pk in assigned_employee_ids if pk is not None and str(pk).strip()] # Add more validation if needed

            if valid_employee_ids:
                try:
                    # Fetch all assigned employees for this assignment entry
                    employees = Employee.objects.filter(pk__in=valid_employee_ids)

                    # Check if all requested employees were actually found
                    if len(employees) != len(valid_employee_ids):
                         found_ids = {str(emp.pk) for emp in employees} # Ensure comparison types match
                         missing_ids = [eid for eid in valid_employee_ids if str(eid) not in found_ids]
                         logging.warning(f"Could not find Employee(s) with IDs: {missing_ids} for assignment {assignment_data} on day {day_str}, shift {service_name}. Skipping creation for these.")

                    # Create ScheduleEvent objects for each found employee
                    for employee_obj in employees:
                        event = ScheduleEvent(
                            schedule=schedule_obj, # Link to the parent schedule object
                            employee=employee_obj,   # Link to the assigned employee
                            date=day_str,
                            start_time=start_time_str,
                            end_time=end_time_str,
                            color=random.choice(ScheduleEvent.COLORS)
                        )
                        events_to_create.append(event)

                except Exception as e:
                    # Catch errors during employee fetching or event creation for this assignment
                    logging.error(f"Error processing employees for assignment {assignment_data} on day {day_str}, shift {service_name}: {e}")
                    # Continue to the next assignment, rather than stopping the whole day or process

    # 4. Bulk create the events in the database for efficiency
    if events_to_create:
        try:
            ScheduleEvent.objects.bulk_create(events_to_create)
            logging.info(f"Successfully created {len(events_to_create)} schedule events.")
            schedule_obj.processed = True
            schedule_obj.save()
        except Exception as e:
            logging.error(f"Error during bulk creation of ScheduleEvents: {e}")
    else:
        logging.info("No schedule events were generated from the provided data.")


