import json
from datetime import date as _date
from pprint import pprint

import mysql.connector
import requests
from api.models import Schedule,Employee

from pathlib import Path

conn = None
cursor = None

def __init__():
    global conn, cursor

    # Connect to the database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        database="masterplan",
        password="123456",
    )



    cursor = conn.cursor()

    database_name = "masterplan"
    # Drop the database if it exists
    cursor.execute(f"DROP DATABASE IF EXISTS {database_name}")
    print(f"Dropped database {database_name} if it existed.")

    # Create a new database
    cursor.execute(f"CREATE DATABASE {database_name}")
    print(f"Created database {database_name}.")

    # Select the new database for further operations
    conn.database = database_name
    path = Path(__file__).parent.parent
    utils_path = path / "utils_files"
    schema = utils_path / "masterplan_base.sql"

    with open(str(schema), 'r', encoding='utf-8') as file:
        sql_script = file.read()

    statements = sql_script.split(';')
    for statement in statements:
        stmt = statement.strip()
        if stmt:
            try:
                cursor.execute(stmt)
            except mysql.connector.Error as err:
                print(f"Error executing statement: {stmt}")
                print(f"MySQL Error: {err}")

    # Commit changes and close connections
    conn.commit()







from random import randint, choice


def insert_role(role_name, max_hours_per_day,max_shifts_per_week,max_hours_per_week,max_hours_per_month):
    role_data = {
        "title": role_name,
        "max_hours_per_day": max_hours_per_day,
        "max_services_per_week": max_shifts_per_week,
        "max_hours_per_week": max_hours_per_week,
        "max_hours_per_month": max_hours_per_month,
    }

    # Query to insert a role
    query = """
    INSERT INTO Role (title, max_hours_per_day, max_services_per_week, max_hours_per_week, max_hours_per_month)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (
        role_data["title"],
        role_data["max_hours_per_day"],
        role_data["max_services_per_week"],
        role_data["max_hours_per_week"],
        role_data["max_hours_per_month"]
    )

    # Execute the query
    cursor.execute(query, values)

    # Commit the changes
    conn.commit()

    return cursor.lastrowid

def create_roster():
    # Query to create a new roster
    r = randint(1, 100)
    query = """
    INSERT INTO Roster (title, autoplan_logic, ignore_working_hours, icsmail_sender_name, icsmail_sender_address)
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        f"Roster {r}",
        1,
        0,
        "None",
        "None",
    )

    # Execute the query
    cursor.execute(query, values)

    # Commit the changes
    conn.commit()

    # Print the inserted row ID
    print(f"Inserted roster with ID: {cursor.lastrowid}")

    return cursor.lastrowid




def insert_employee(roster_id, role_crm_id, employee, role, absences):
    # Query to insert an employee
    query = """
    INSERT INTO User (superadmin, login, firstname, lastname, fullname, 
                          birthday, start_date, password, ldap, locked, 
                          max_hours_per_day, max_services_per_week, max_hours_per_week, 
                          max_hours_per_month, color)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

    """
    values = (
        0, # superadmin
        f"{employee.id}{employee.id}", # login
        employee.id, # first name
        employee.id, # last name
        f"{employee.id} {employee.id}", # full name
        None, # birthday
        None, # start date
        None, # password
        0, # ldap
        0, # locked
        role.max_hours_per_day,
        role.max_services_per_week,
        role.max_hours_per_week,
        role.max_hours_per_month,
        '#FFFFFF',
    )

    # Execute the query
    cursor.execute(query, values)

    # Commit the changes
    conn.commit()

    # Print the inserted row ID
    print(f"Inserted employee with ID: {cursor.lastrowid}")
    employee_crm_id = cursor.lastrowid
    # Query to insert a record into UserToRoster
    query = """
    INSERT INTO UserToRoster (user_id, roster_id)
    VALUES (%s, %s)
    """
    values = (
        employee_crm_id,
        roster_id
    )

    # Execute the query
    cursor.execute(query, values)

    # Commit the changes
    conn.commit()

    # Print the inserted row ID
    print(f"Inserted record into UserToRoster with user_id: {employee_crm_id} and roster_id: {roster_id}")

    # Query to insert a record into UserToRole
    query = """
    INSERT INTO UserToRole (user_id, role_id)
    VALUES (%s, %s)
    """
    values = (
        employee_crm_id,
        role_crm_id
    )

    # Execute the query
    cursor.execute(query, values)

    # Commit the changes
    conn.commit()
    '''
    for absence in absences:
        absence_start = absence
        absence_end = absence
        absence_start_time = None
        absence_end_time = None
        absence_comment = "12345"
        absence_approved1 = 0
        absence_approved2 = 0
        approved1_by_user_id = None
        approved2_by_user_id = None
        # Query to insert absence data
        query = """
        INSERT INTO Absence (user_id, absent_type_id, submitted, start, end, start_time, end_time, comment, approved1, approved2, approved1_by_user_id, approved2_by_user_id)
        VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            employee_crm_id,  # user_id
            1,  # absent_type_id
            absence_start,  # start
            absence_end,  # end
            absence_start_time,  # start_time (can be NULL)
            absence_end_time,  # end_time (can be NULL)
            absence_comment,  # comment
            absence_approved1,  # approved1 (0 or 1)
            absence_approved2,  # approved2 (0 or 1)
            approved1_by_user_id,  # approved1_by_user_id (can be NULL)
            approved2_by_user_id  # approved2_by_user_id (can be NULL)
        )

        # Execute the query
        cursor.execute(query, values)

        # Commit the changes
        conn.commit()
        '''
    # Print the inserted row ID
    print(f"Inserted record into UserToRole with user_id: {employee_crm_id} and role_id: {role_crm_id}")

    return employee_crm_id



def insert_service(roster_id, name, min_employees, start, end):
    # Query to insert a record into Service
    query = """
    INSERT INTO Service (roster_id, shortname, title, location, employees, start, end, date_start, date_end, color, wd1, wd2, wd3, wd4, wd5, wd6, wd7)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        roster_id,
        name,
        name,
        "location",
        min_employees,
        start,
        end,
        "2000-01-01",
        "2100-01-01",
        "FFFFFF",
        1,
        1,
        1,
        1,
        1,
        1,
        1
    )

    # Execute the query
    cursor.execute(query, values)

    # Commit the changes
    conn.commit()

    # Print the inserted row ID
    print(f"Inserted service with ID: {cursor.lastrowid}")


def merge_services(data):
    """
    Merges multiple entries (employee lists) for the same service_name
    under each date into a single entry with a combined employees list.
    Ensures every day has all service names observed in the entire dataset,
    inserting an empty list of employees for services missing on a specific day.

    :param data: A dict of the form:
                 {
                     "2025-02-01": [
                         {"service_name": "Mattina", "employees": ["12"]},
                         {"service_name": "Mattina", "employees": ["10"]},
                         ...
                     ],
                     "2025-02-02": [...],
                     ...
                 }
    :return: A dict of the same structure, but with merged employee lists
             for each distinct service_name under a date, and a placeholder
             (empty list) for missing service_names on any date.
             Example:
             {
                 "2025-02-01": [
                     {"service_name": "Mattina", "employees": ["10", "12", ...]},
                     {"service_name": "Pomeriggio", "employees": []},  # if missing
                     ...
                 ],
                 ...
             }
    """
    # First pass: gather all distinct service names across all days
    all_services = set()
    for services_list in data.values():
        for entry in services_list:
            all_services.add(entry["service_name"])

    merged_data = {}

    # For each day...
    for date_str, services_list in data.items():
        service_dict = {}

        # Merge employees for each service_name
        for entry in services_list:
            service_name = entry["service_name"]
            employees = entry["employees"]
            if service_name not in service_dict:
                service_dict[service_name] = set()
            service_dict[service_name].update(employees)

        # Now ensure that every service in all_services is present
        day_services = []
        for service_name in all_services:
            if service_name in service_dict:
                # Convert the set to a list (could be sorted if desired)
                employees_list = list(service_dict[service_name])
            else:
                # Service is missing for this day, so use an empty list
                employees_list = []

            day_services.append({
                "service_name": service_name,
                "employees": employees_list
            })

        merged_data[date_str] = day_services

    return merged_data


def create_scheduleMP(orario_id):
        schedule = Schedule.objects.get(id=orario_id)
        employees = Employee.objects.filter(id__in=schedule.employees).select_related('role')
        shifts_data = schedule.shift_data
        shift_types = [shift['name'] for shift in shifts_data]
        free_days = schedule.free_days

        used_roles = list(set([employee.role for employee in employees]))

        '''
        for role in used_roles:
            print(role.__dict__)

        for employee in employees:
            print(employee.__dict__)

        for shift_data in shifts_data:
            print(shift_data)

        for free_day in free_days:
            print(free_days[free_day])

        for role in used_roles:
            print("ROLE", role.__dict__)
        '''

        roster_id = create_roster()

        employees_crm = {}

        for role in used_roles:
            role_id = insert_role(role.name, role.max_hours_per_day, role.max_services_per_week, role.max_hours_per_week, role.max_hours_per_month)
            current_employees = employees.filter(role=role)
            for employee in current_employees:
                for item in free_days:
                    for k,v in item.items():
                        if item['employee_id'] == employee.id:
                            employee_crm_id = insert_employee(roster_id, role_id, employee, role, free_days.index(item))
                            employees_crm[employee.id] = employee_crm_id

        for shift_data in shifts_data:
            insert_service(roster_id, shift_data['name'], shift_data['minEmployees'], shift_data['start'], shift_data['end'])

        # Define base URL and parameters

        import requests

        # Initialize a session
        session = requests.Session()

        # Step 1: Perform login
        login_request_url = "http://localhost/masterplan/frontend/login.php"
        login_data = {
            "username": "root",
            "password": "123456"
        }

        # Send POST request for login; the session object will store cookies (including PHPSESSID)
        login_response = session.post(login_request_url, data=login_data)

        # Retrieve the PHPSESSID if needed
        php_session_id = session.cookies.get("PHPSESSID")
        print("Logged in with PHPSESSID:", php_session_id)

        # Step 2: Use the session for subsequent requests

        response = session.get("http://localhost/masterplan/frontend/index.php", params={
            "view": "plan",
            "roster": roster_id,  # replace with actual roster_id
            "week": "",
            "timespan": "flex",
            "start": schedule.start_date,  # example start_date; use orarioschedulestart_date
            "end": schedule.end_date  # example end_date; use orarioscheduleend_date
        })

        # Define base URL and parameters for the next request
        base_url = "http://localhost/masterplan/frontend/index.php"
        params = {
            "view": "plan",
            "roster": roster_id,  # replace with actual roster_id
            "week": "",
            "timespan": "flex",
            "start": schedule.start_date,  # example start_date; use orarioschedulestart_date
            "end": schedule.end_date  # example end_date; use orarioscheduleend_date
        }

        # Define form-data payload for the next request
        data = {
            "action": "autoplan_services",
            "roster": roster_id,  # replace with actual roster_id
            "start_date": schedule.start_date,  # use orarioschedulestart_date
            "end_date": schedule.end_date  # use orarioscheduleend_date
        }

        # Use the same session to make the post request; cookies are automatically included
        response = session.post(base_url, params=params, data=data)

        # Check response status or content

        if response.status_code == 200:
            # Execute query to retrieve services within date range
            query = """
            SELECT *
            FROM PlannedService
            WHERE day BETWEEN %s AND %s;
            """
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (schedule.start_date, schedule.end_date))
            services = cursor.fetchall()

            service_query = "SELECT id, shortname FROM Service;"
            cursor.execute(service_query)
            service_rows = cursor.fetchall()
            shift_types = { item['id']: item['shortname'] for item in service_rows }

            user_query = "SELECT * FROM User;"
            cursor.execute(user_query)
            users = cursor.fetchall()
            users_crm = { item['id']: item['firstname'] for item in users }

            services_data = {}
            for row in services:
                # Use a consistent string key for the day
                date_key = row['day'].strftime("%Y-%m-%d")

                # Initialize the list for this date if not already present
                if date_key not in services_data:
                    services_data[date_key] = []

                # Prepare the data entry for the current row
                data = {
                    'service_name': shift_types[row['service_id']],
                    'employees': [users_crm[row['user_id']]]
                }

                # Append the data to the list for this date
                services_data[date_key].append(data)

            merged_data = merge_services(services_data)

            pprint(merged_data)

            def parse_time_to_minutes(timestr):
                """ Convert 'HH:MM' to total minutes from midnight. E.g. '9:00' -> 540 """
                hours, mins = timestr.split(':')
                return int(hours) * 60 + int(mins)

            SHIFT_DEFINITIONS = schedule.shift_data

            # Build a dictionary for quick shift lookup by shift name
            SHIFTS_BY_NAME = {}
            for shift in SHIFT_DEFINITIONS:
                SHIFTS_BY_NAME[shift["name"]] = {
                    "start": parse_time_to_minutes(shift["start"]),
                    "end": parse_time_to_minutes(shift["end"])
                }

            def generate_timeline(schedule_data):
                """
                schedule_data is something like:
                {
                  "2025-02-01": [
                      {"service_name": "Mattina", "employees": ["2", "4"]},
                      {"service_name": "Pomeriggio", "employees": ["3"]},
                      {"service_name": "Chiusura", "employees": ["3"]}
                  ],
                  "2025-02-02": [...],
                  ...
                }

                Returns a structure that is easier to render in a half-hour timeline:
                {
                  "2025-02-01": {
                    540: ["2", "4"],      #  9:00
                    570: ["2", "4"],      #  9:30
                    600: ["2", "4"],      # 10:00
                    ...
                    780: ["3"],           # 13:00 - 13:30 belongs to "Pomeriggio"
                    ...
                  },
                  "2025-02-02": { ... }
                }
                Each key in the day dictionary is the minute-of-day for each half hour slot.
                Each value is a list of employees on shift for that slot.
                """
                # We assume the earliest shift starts at 9:00 (540) and the latest ends at 20:00 (1200).
                start_of_day = 540  # 9:00 in minutes
                end_of_day = 1200  # 20:00 in minutes
                step = 30  # half-hour increments

                # The final structure
                day_timeline_map = {}

                for date_str, shift_assignments in schedule_data.items():
                    # For each day, prepare a dictionary with every half-hour slot from 9:00 to 20:00
                    half_hours = {m: [] for m in range(start_of_day, end_of_day + step, step)}

                    # shift_assignments is a list of dicts with "service_name" and "employees"
                    for assignment in shift_assignments:
                        shift_name = assignment["service_name"]
                        employees = assignment["employees"]

                        # Look up the shift start/end in minutes
                        shift_info = SHIFTS_BY_NAME.get(shift_name)
                        if not shift_info:
                            continue  # skip if the shift name doesn't match known definitions

                        s_start = shift_info["start"]  # e.g. 540 for 9:00
                        s_end = shift_info["end"]  # e.g. 780 for 13:00

                        # Populate the employees for each half-hour slot that falls within [s_start, s_end)
                        for minute_mark in range(start_of_day, end_of_day, step):
                            if s_start <= minute_mark < s_end:
                                # Extend the list of employees for that half-hour slot
                                half_hours[minute_mark].extend(employees)

                    # Save the half-hour mapping for this day
                    day_timeline_map[date_str] = half_hours

                return day_timeline_map

            timeline_map = generate_timeline(merged_data)


            schedule.schedule_data = json.dumps(timeline_map)
            schedule.processed = True # TODO: set to true
            schedule.save()

            return 0

        else:
            print("no")


__init__()








