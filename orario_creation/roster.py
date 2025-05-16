import logging
from random import randint

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

def get_roster_data(cursor, conn, session, roster_id, schedule):

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

    return services_data

def start_planning(session, roster_id, schedule):

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
        print("Request successful")
    else:
        print("Request failed with status code:", response.status_code)


