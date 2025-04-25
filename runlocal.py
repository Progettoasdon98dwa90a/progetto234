
def main():
    import os
    import sys
    from pathlib import Path

    # Get the current working directory
    current_directory = Path(__file__).resolve().parent

    # Add the parent directory to the system path
    sys.path.append(str(current_directory.parent))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionale.settings.local')
    os.environ.setdefault('SECRET_KEY', 'django-insecure-2b7l^qo9t-8u8)5b4n0$%3b*3w0u$)g4$%z*!s%v7_1&2jx1')

    SEED_DATA = False

    import django
    django.setup()

    from django.core.management import call_command


    if SEED_DATA:
        call_command('makemigrations', 'api', interactive=False)  # Apply migrations
        call_command('migrate')  # Apply migrations
        print("Migrations applied successfully.")
        # Flush the database
        call_command('flush', interactive=False)

        call_command('seed')
        print("Seed data loaded successfully.")



    call_command('collectstatic', interactive=False)
    print("Static files collected successfully.")



    # Run the Django development server
    call_command('runserver')


if __name__ == "__main__":
    main()
    # main()