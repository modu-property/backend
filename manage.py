#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    settings = None
    if os.getenv("SERVER_ENV") == "prod":
        settings = "modu_property.prod_settings"
    elif os.getenv("SERVER_ENV") == "local":
        settings = "modu_property.local_settings"
    elif os.getenv("SERVER_ENV") == "test":
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
