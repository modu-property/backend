import os

from celery import Celery

settings = None
if os.getenv("SERVER_ENV") == "prod":
    settings = "modu_property.prod_settings"
elif os.getenv("SERVER_ENV") == "local":
    settings = "modu_property.local_settings"
elif os.getenv("SERVER_ENV") == "test":
    settings = "modu_property.test_settings"

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

app = Celery("modu_property")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
