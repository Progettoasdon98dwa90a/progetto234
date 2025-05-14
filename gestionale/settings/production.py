import os

from .base import *

import dj_database_url

SECRET_KEY = os.getenv('SECRET_KEY')

DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,  # Enable connection health checks
            ssl_require=True,  # Force SSL
        )
    }

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["progetto234-production-4b44.up.railway.app"]
CORS_ALLOW_ALL_ORIGINS = True

SESSION_COOKIE_HTTPONLY = True  # ✔️ Enable for security
SESSION_COOKIE_SAMESITE = 'Lax'  # ✔️ Add this
SESSION_COOKIE_DOMAIN = '.progetto234-production-4b44.up.railway.app'  # ✔️ Wildcard domain

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True  # Set back to True after HTTPS works
SECURE_SSL_REDIRECT = True

SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Add this
# Security settings
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

QR_DOMAIN_NAME= 'https://progetto234-production-4b44.up.railway.app'
MEDIA_URL = ''


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
