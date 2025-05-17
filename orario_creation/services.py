def insert_shift(cursor, conn, roster_id, name,
                 min_employees, date_start, date_end, time_start, time_end):

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
        time_start,
        time_end,
        date_start,
        date_end,
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

    # TODO: INSERIRE I PARTICULAR_DAYS CON I DIPENDENTI MAGGIORATI

    # Print the inserted row ID
    print(f"Inserted service with ID: {cursor.lastrowid}")