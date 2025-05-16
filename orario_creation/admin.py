import requests
from django.conf import settings

masterplan_app = settings.MASTERPLAN_APP
masterplan_port = settings.MASTERPLAN_PORT

def insert_admin(cursor, conn):
    admin_data = {
        "superadmin": 1,
        "login": "masterplan",
        "firstname": "",
        "lastname": "",
        "fullname": "Administrator",
        "email": "",
        "phone": "",
        "mobile": "",
        "birthday": None,
        "start_date": "2025-04-10",
        "id_no": "",
        "description": "initial admin user",
        "password": "$2y$10$v8fFaK6i6tedtW.IdT6sHeoK23nMfRxdQyoRRBNvmn/hjka/zYKBG",
        "ldap": False,
        "locked": False,
        "max_hours_per_day": -1,
        "max_services_per_week": -1,
        "max_hours_per_week": -1,
        "max_hours_per_month": -1,
        "color": "#fff"
    }

    # Query to insert an admin
    query = """
    INSERT INTO `User` (
        `superadmin`, `login`, `firstname`, `lastname`, `fullname`, 
        `email`, `phone`, `mobile`, `birthday`, `start_date`, `id_no`, 
        `description`, `password`, `ldap`, `locked`, `max_hours_per_day`, 
        `max_services_per_week`, `max_hours_per_week`, `max_hours_per_month`, `color`
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """

    values = (
        admin_data["superadmin"],
        admin_data["login"],
        admin_data["firstname"],
        admin_data["lastname"],
        admin_data["fullname"],
        admin_data["email"],
        admin_data["phone"],
        admin_data["mobile"],
        admin_data["birthday"],
        admin_data["start_date"],
        admin_data["id_no"],
        admin_data["description"],
        admin_data["password"],
        admin_data["ldap"],
        admin_data["locked"],
        admin_data["max_hours_per_day"],
        admin_data["max_services_per_week"],
        admin_data["max_hours_per_week"],
        admin_data["max_hours_per_month"],
        admin_data["color"]
    )

    # Execute the query
    cursor.execute(query, values)

    # Commit the changes
    conn.commit()

    login_data = {
        "username": "masterplan",
        "password": "PASSWORD"
    }
    session = requests.Session()

    login_request_url = f"http://{masterplan_app}:{masterplan_port}/masterplan/frontend/login.php"

    session.post(login_request_url, data=login_data)


    return session
