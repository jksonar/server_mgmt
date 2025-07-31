"""
WSGI config for server_mgmt project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

# Set the DJANGO_ENV environment variable. Default to 'prod' for WSGI.
os.environ.setdefault('DJANGO_ENV', 'prod')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server_mgmt.settings')

application = get_wsgi_application()
