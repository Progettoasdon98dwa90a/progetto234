import os
import sys
from pathlib import Path
import django
import dj_database_url
import psycopg2
from django.core.management import call_command

def reset_schema():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise Exception("DATABASE_URL environment variable not set")

    db = dj_database_url.parse(db_url)

    conn = psycopg2.connect(
        dbname=db.get('NAME'), # Use .get() for safety
        user=db.get('USER'),
        password=db.get('PASSWORD'),
        host=db.get('HOST'),
        port=db.get('PORT'),
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("DROP SCHEMA public CASCADE;")
        cur.execute("CREATE SCHEMA public;")
    conn.close()

def main():
    current_directory = Path(__file__).resolve().parent

    sys.path.append(str(current_directory.parent))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionale.settings.local')
    os.environ.setdefault('SECRET_KEY', 'django-insecure-2b7l^qo9t-8u8)5b4n0$%3b*3w0u$)g4$%z*!s%v7_1&2jx1')
    os.environ.setdefault('POSTGRES', 'True')
    os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:12345678@localhost:5432/postgres')

    SEED_DATA = True

    django.setup()

    is_reloader_child = os.environ.get('RUN_MAIN') == 'true'

    if not is_reloader_child:
        print("Running initial setup (migrations, seeding, static)...")

        if SEED_DATA:
            reset_schema()
            print("Schema dropped and created successfully.")
            call_command('migrate')  # Apply migrations
            print("Migrations applied successfully.")
            call_command('seed') # Load seed data
            print("Seed data loaded successfully.")

        call_command('collectstatic', interactive=False)
        print("Static files collected successfully.")

        print("Initial setup complete. Handing off to runserver...")
    else:
        print("Running in reloader child process - skipping setup.")


    print("Starting Django development server...")
    call_command('runserver', '0.0.0.0:8000')
    print("Server command finished.") # This line is reached when the server is stopped

if __name__ == "__main__":
    main()