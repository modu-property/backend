import os

from celery import Celery


server_env = os.getenv("SERVER_ENV")
print(f"SERVER_ENV : {server_env}")
settings = f"modu_property.settings.{server_env}_settings"

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
