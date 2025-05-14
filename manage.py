#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionale.settings.local')
    os.environ.setdefault('SECRET_KEY', 'django-insecure-2b7l^qo9t-8u8)5b4n0$%3b*3w0u$)g4$%z*!s%v7_1&2jx1')
    os.environ.setdefault('POSTGRES', 'True')
    os.environ.setdefault('DATABASE_URL', 'postgresql://localhost:5432/postgres?user=postgres&password=12345678')


    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
