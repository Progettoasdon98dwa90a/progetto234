from datetime import datetime, timedelta

from orario_creation.absence import insert_absence
from orario_creation.admin import insert_admin
from orario_creation import initialize_database
from orario_creation.employees import insert_employee
from orario_creation.services import insert_shift
from orario_creation.roles import insert_role
from orario_creation.roster import create_roster, get_roster_data, start_planning
from django.conf import settings
import requests

import logging
masterplan_app = settings.MASTERPLAN_APP
masterplan_port = settings.MASTERPLAN_PORT

logger = logging.getLogger('procrastinate')

def fill_data_and_create_schedule(schedule_obj):

    schedule_data = schedule_obj.create_payload()

    logging.info("Creating schedule...")

    logging.info("Initializing database...")
    conn, cursor = initialize_database()
    logging.info("Database initialized...")

    logging.info('creating admin...')
    session = insert_admin(cursor,conn)
    logging.info('admin created...')

    logging.info('creating roster...')
    roster_id = create_roster(cursor, conn)
    logging.info('roster created...')

    logging.info('creating employees...')
    for employee_id, employee_data in schedule_data['employees'].items():

        role_mp_id = insert_role(
            cursor,
            conn,
            employee_data['id'],
            employee_data['max_hours_per_day'],
            employee_data['max_services_per_week'],
            employee_data['max_hours_per_week'],
            employee_data['max_hours_per_month']
        )

        employee_mp_id = insert_employee(
            cursor,
            conn,
            roster_id,
            role_mp_id,
            employee_data,
            []
        )

    logging.info('employees created...')

    # [{"2025-08-01": [2, "P"]}, {"2025-08-02": [1, "M"]}, {"2025-08-03": [1, "C"]}] example particular days

    logging.info('inserting services...')

    # for days from start_date to end_date
    start_date = schedule_obj.start_date
    end_date = schedule_obj.end_date

    try:
        start_date_obj = datetime.strptime(schedule_obj.start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(schedule_obj.end_date, "%Y-%m-%d").date()
    except ValueError as e:
        logging.error(f"Invalid date format: {e}")
        return

    if start_date_obj > end_date_obj:
        logging.warning(f"Start date {start_date_obj} is after end date {end_date_obj}. No shifts to process.")
        return

    logging.info(f"Overall schedule range: {start_date_obj} to {end_date_obj}")

    # Prepare particular days: convert string dates to date objects and sort them
    particular_days_dates = []
    if 'particular_days' in schedule_data and schedule_data['particular_days']:
        for date_str in schedule_data['particular_days'].keys():
            try:
                pd_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if start_date_obj <= pd_date <= end_date_obj:  # Only consider PDs within the schedule range
                    particular_days_dates.append(pd_date)
            except ValueError:
                logging.warning(f"Skipping invalid date format in particular_days: {date_str}")
        particular_days_dates.sort()

    logging.info(f"Sorted particular days within range: {particular_days_dates}")

    # --- Helper function to insert standard shifts for a given period ---
    def _insert_standard_shifts_for_period(period_start_date, period_end_date, shifts_data_map):
        if period_start_date > period_end_date:
            return  # No period to process

        logging.info(f"--- Processing STANDARD shifts for period: {period_start_date} to {period_end_date} ---")
        for shift_name, shift_details in shifts_data_map.items():
            employees = int(shift_details.get('minEmployees', 0))
            start_time = shift_details.get('start', '00:00')
            end_time = shift_details.get('end', '23:59')

            insert_shift(cursor, conn, roster_id,
                         shift_name, employees,
                         period_start_date.strftime("%Y-%m-%d"),
                         period_end_date.strftime("%Y-%m-%d"),
                         start_time, end_time)

    # --- Main processing logic ---
    current_segment_start_date = start_date_obj

    for pd_date_obj in particular_days_dates:
        # 1. Process normal shifts BEFORE this particular day
        # The end of the normal segment is the day before the particular day
        normal_segment_end_date = pd_date_obj - timedelta(days=1)

        if current_segment_start_date <= normal_segment_end_date:
            _insert_standard_shifts_for_period(
                current_segment_start_date,
                normal_segment_end_date,
                schedule_data.get('shifts_data', {})
            )

        # 2. Process the PARTICULAR DAY itself
        logging.info(f"--- Processing PARTICULAR day: {pd_date_obj} ---")
        pd_date_str = pd_date_obj.strftime("%Y-%m-%d")
        pd_config = schedule_data['particular_days'].get(pd_date_str, [0, None])
        pd_employees_to_add = pd_config[0]
        pd_target_shift_name = pd_config[1]

        logging.info(
            f"Particular Day Config for {pd_date_str}: Employees to add={pd_employees_to_add}, Target Shift='{pd_target_shift_name}'")

        for shift_name, shift_details in schedule_data.get('shifts_data', {}).items():
            employees = int(shift_details.get('minEmployees', 0))
            start_time = shift_details.get('start', '00:00')
            end_time = shift_details.get('end', '23:59')

            # Add extra employees if this is the target shift for the particular day
            if shift_name == pd_target_shift_name:
                employees += pd_employees_to_add
                logging.info(
                    f"  Augmenting shift '{shift_name}' with {pd_employees_to_add} employees. Total: {employees}")

            insert_shift(cursor, conn, roster_id,
                         shift_name, employees,
                         pd_date_str, pd_date_str,  # Start and end on the same particular day
                         start_time, end_time)

        # Update the start for the next segment
        current_segment_start_date = pd_date_obj + timedelta(days=1)

    # 3. Process any remaining normal shifts AFTER the last particular day (or if no particular days)
    if current_segment_start_date <= end_date_obj:
        _insert_standard_shifts_for_period(
            current_segment_start_date,
            end_date_obj,
            schedule_data.get('shifts_data', {})
        )

    logging.info('services inserted...')
    ### END INSERTING DATA IN DB

    logging.info('starting planning...')
    start_planning(session, roster_id, schedule_obj)
    logging.info('planning finished...')

    logging.info('setting absences for employees...')
    for employee_free_days_data in schedule_data['free_days']:
        insert_absence(session, employee_free_days_data)
        print(f"Absence inserted for {employee_free_days_data['employee_id']} on {employee_free_days_data['dates']}")

    logging.info("Getting roster data...")
    result = get_roster_data(cursor, conn,session, roster_id, schedule_obj)
    logging.info("Schedule created...")
    return result



