import logging
from random import randint

import requests
from django.conf import settings

masterplan_app = settings.MASTERPLAN_APP
masterplan_port = settings.MASTERPLAN_PORT

logger = logging.getLogger('procrastinate')

def create_roster(cursor, conn):
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

def get_roster_data(cursor, conn, roster_id, schedule):
    login_data = {
        "username": "masterplan",
        "password": "PASSWORD"
    }
    session = requests.Session()

    login_request_url = f"http://{masterplan_app}:{masterplan_port}/masterplan/frontend/login.php"

    # Send POST request for login; the session object will store cookies (including PHPSESSID)
    login_response = session.post(login_request_url, data=login_data)

    # Retrieve the PHPSESSID if needed
    php_session_id = session.cookies.get("PHPSESSID")
    print("Logged in with PHPSESSID:", php_session_id)

    # Step 2: Use the session for subsequent requests

    response = session.get(f"http://{masterplan_app}:{masterplan_port}/masterplan/frontend/index.php", params={
        "view": "plan",
        "roster": roster_id,  # replace with actual roster_id
        "week": "",
        "timespan": "flex",
        "start": schedule.start_date,  # example start_date; use orarioschedulestart_date
        "end": schedule.end_date  # example end_date; use orarioscheduleend_date
    })

    # Define base URL and parameters for the next request
    base_url = f"http://{masterplan_app}:{masterplan_port}/masterplan/frontend/index.php"
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
        shift_types = {item['id']: item['shortname'] for item in service_rows}

        user_query = "SELECT * FROM User;"
        cursor.execute(user_query)
        users = cursor.fetchall()
        users_crm = {item['id']: item['firstname'] for item in users}

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

        return services_data

    else:
        logging.error(f"Error: {response.status_code}")
        logging.error(f"Response content: {response.content}")
        return 1

    conn.close()

    return 1

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