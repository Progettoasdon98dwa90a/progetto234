def insert_employee(cursor, conn, roster_id, role_crm_id, employee_data, absences):
    # Query to insert an employee
    query = """
    INSERT INTO User (superadmin, login, firstname, lastname, fullname, 
                          birthday, start_date, password, ldap, locked, 
                          max_hours_per_day, max_services_per_week, max_hours_per_week, 
                          max_hours_per_month, color)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

    """
    values = (
        0,  # superadmin
        f"{employee_data['id']}{employee_data['id']}",  # login
        employee_data['id'],  # first name
        employee_data['id'],  # last name
        f"{employee_data['id']} {employee_data['id']}",  # full name
        None,  # birthday
        None,  # start date
        None,  # password
        0,  # ldap
        0,  # locked
        employee_data['max_hours_per_day'],
        employee_data['max_services_per_week'],
        employee_data['max_hours_per_week'],
        employee_data['max_hours_per_month'],
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

    # Print the inserted row ID
    print(f"Inserted record into UserToRole with user_id: {employee_crm_id} and role_id: {role_crm_id}")

    return employee_crm_id