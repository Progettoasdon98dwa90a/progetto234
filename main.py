import os

import django
from gunicorn.app.base import BaseApplication
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command
import dj_database_url
import psycopg2


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


class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application



if __name__ == '__main__':
    # Set the Django settings module
    django.setup()

    if os.getenv('DJANGO_SEED') == 'True':
        reset_schema()
        print("OK RESET SCHEMA")

    # Run Django migrations
    call_command('migrate')
    print("OK MIGRATION")
    if os.getenv('DJANGO_SEED') == 'True':
        # Load initial data
        call_command('seed')
        print("OK SEED")

    call_command('collectstatic', interactive=False)
    print("OK CLLSTC")


    # Get the WSGI application
    application = get_wsgi_application()
    # Gunicorn configuration options
    options = {
        'bind': '0.0.0.0:8000',  # Bind to all interfaces on port 8000
        'workers': 3,             # Number of worker processes
        'accesslog': '-',         # Log access to stdout
        'errorlog': '-',          # Log errors to stderr
    }

    StandaloneApplication(application, options).run()
