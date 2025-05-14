from pathlib import Path
import mysql.connector

conn = None
cursor = None
masterplan_app = None

def initialize_database():
    global conn, cursor, masterplan_app

    # Connect to the database
    conn = mysql.connector.connect(
        host='localhost',
        user="masterplan",
        database="masterplan",
        password="PASSWORD",
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

    return conn, cursor

if __name__ == "__main__":
    initialize_database()

