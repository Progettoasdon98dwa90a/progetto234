import os
import subprocess
import sys
from pathlib import Path
import django
import dj_database_url
import psycopg2
from django.conf import settings
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

    SEED_DATA = False
    worker_process = None

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

        # --- Start the Procrastinate worker process ---
        print("Starting Procrastinate worker...")
        worker_command = [
            sys.executable,  # Use the same python interpreter
            settings.BASE_DIR / 'manage.py',
            'procrastinate',
            'worker',
        ]
        # Use subprocess.Popen to start the worker non-blocking
        worker_process = subprocess.Popen(
            worker_command,
            cwd=settings.BASE_DIR,  # Run the command from the project root
            env=os.environ.copy(),  # Pass the current environment variables
            # Optional: Redirect stdout/stderr for cleaner output or logging
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
        )
        print(f"Procrastinate worker started with PID: {worker_process.pid}")

        print("Initial setup complete. Handing off to runserver...")
    else:
        print("Running in reloader child process - skipping setup.")


    print("Starting Django development server...")
    call_command('runserver', '0.0.0.0:8000')

    if worker_process and worker_process.poll() is None:  # Check if the process is still running
        print(f"Terminating Procrastinate worker (PID: {worker_process.pid})...")
        try:
            # Send SIGTERM for graceful shutdown
            worker_process.terminate()
            # Wait for the worker to exit, with a timeout
            worker_process.wait(timeout=10)  # Wait up to 10 seconds
            print("Procrastinate worker terminated gracefully.")
        except subprocess.TimeoutExpired:
            # If worker doesn't exit after timeout, force kill
            print("Procrastinate worker did not terminate gracefully, killing...", file=sys.stderr)
            worker_process.kill()  # Send SIGKILL
            worker_process.wait()  # Wait for kill to complete
            print("Procrastinate worker killed.")
        except Exception as e:
            print(f"An error occurred while terminating worker: {e}", file=sys.stderr)
    elif worker_process:
        print(f"Procrastinate worker (PID: {worker_process.pid}) was already stopped.")

    print("Server command finished.") # This line is reached when the server is stopped

if __name__ == "__main__":
    main()