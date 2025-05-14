

def insert_role(cursor, conn, role_name, max_hours_per_day, max_shifts_per_week, max_hours_per_week, max_hours_per_month):
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