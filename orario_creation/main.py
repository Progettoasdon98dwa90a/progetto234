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

    particular_days = schedule_data['particular_days']
    # [{"2025-08-01": [2, "P"]}, {"2025-08-02": [1, "M"]}, {"2025-08-03": [1, "C"]}] example particular days


    logging.info('inserting services...')
    for shift_name, shift_data in schedule_data['shifts_data'].items():
        logging.info(shift_data)
        insert_shift(cursor, conn, roster_id,
                     shift_name, shift_data['minEmployees'], shift_data['start'], shift_data['end'],
                     )

    logging.info(schedule_data['periods'])


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



