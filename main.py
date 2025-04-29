import django
from gunicorn.app.base import BaseApplication
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command


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

    # Flush the database
    # call_command('flush', interactive=False)  # Flush the database
    print("OK FLUSH")
    # Run Django migrations
    call_command('migrate')
    print("OK MIGRATION")
    # Load initial data
    # call_command('seed')
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
