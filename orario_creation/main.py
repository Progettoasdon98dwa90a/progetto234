from orario_creation.admin import insert_admin
from orario_creation import initialize_database
from orario_creation.employees import insert_employee
from orario_creation.services import insert_service
from orario_creation.roles import insert_role
from orario_creation.roster import create_roster, get_roster_data

import logging

logger = logging.getLogger('procrastinate')

def fill_data_and_create_schedule(schedule_obj):

    schedule_data = schedule_obj.create_payload()

    logging.info("Creating schedule...")

    logging.info("Initializing database...")
    conn, cursor = initialize_database()
    logging.info("Database initialized...")

    logging.info('creating admin...')

    insert_admin(cursor,conn)

    logging.info('admin created...')

    logging.info('creating roster...')

    roster_id = create_roster(cursor, conn)

    logging.info('roster created...')

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

    logging.info('inserting services...')
    for service_name, service_data in schedule_data['services'].items():
        logging.info(service_data)
        insert_service(cursor, conn, roster_id, service_name, service_data['minEmployees'], service_data['start'], service_data['end'])

    logging.info('services inserted...')
    result = get_roster_data(cursor, conn, roster_id, schedule_obj)
    logging.info("Schedule created...")
    return result
