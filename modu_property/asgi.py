"""
ASGI config for modu_property project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

settings = None
if os.getenv("SERVER_ENV") == "prod":
    settings = "modu_property.prod_settings"
elif os.getenv("SERVER_ENV") == "local":
    settings = "modu_property.local_settings"
elif os.getenv("SERVER_ENV") == "test":
    settings = "modu_property.test_settings"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

application = get_asgi_application()
