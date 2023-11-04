#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    settings = None
    server_env = os.getenv("SERVER_ENV")
    print(server_env)
    if server_env == "prod":
        settings = "modu_property.prod_settings"
    elif server_env == "local":
        settings = "modu_property.local_settings"
    elif server_env == "test":
        settings = "modu_property.test_settings"

    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
