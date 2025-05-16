def insert_shift(cursor, conn, roster_id, name,
                 min_employees, start, end,
                 is_particular_day=False, extra_employees=None):

    # Query to insert a record into Service (or Shift) with exception for particular days with extra employees
    num_employees = min_employees
    if is_particular_day:
        num_employees += extra_employees


    query = """
    INSERT INTO Service (roster_id, shortname, title, location, employees, start, end, date_start, date_end, color, wd1, wd2, wd3, wd4, wd5, wd6, wd7)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        roster_id,
        name,
        name,
        "location",
        num_employees,
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

    # TODO: INSERIRE I PARTICULAR_DAYS CON I DIPENDENTI MAGGIORATI

    # Print the inserted row ID
    print(f"Inserted service with ID: {cursor.lastrowid}")