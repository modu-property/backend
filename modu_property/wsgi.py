"""
WSGI config for modu_property project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

server_env = os.getenv("SERVER_ENV")
print(f"SERVER_ENV : {server_env}")
settings = f"modu_property.settings.{server_env}_settings"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

application = get_wsgi_application()
