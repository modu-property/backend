from dotenv import load_dotenv

load_dotenv(".env.testing")

from .base_settings import *

file_path = os.path.abspath(__file__)
dir_name = os.path.dirname(file_path)
parent_dir = os.path.dirname(dir_name)


LOGGING["handlers"] = {
    "console": {
        "level": LOG_LEVEL,
        "filters": ["require_debug_true"],
        "class": "logging.StreamHandler",
    },
    "django.server": {  # python manage.py runserver로 작동하는 개발 서버에서만 사용하는 핸들러로 콘솔에 로그를 출력
        "level": LOG_LEVEL,
        "class": "logging.StreamHandler",
        "formatter": "django.server",
    },
    "file": {
        "level": LOG_LEVEL,
        "filters": ["require_debug_true"],
        "class": "logging.handlers.RotatingFileHandler",
        "filename": f"{parent_dir}/logs/modu_property.log",
        "maxBytes": 1024 * 1024 * 50,  # 50 MB
        "backupCount": 5,
        "formatter": "django.server",
    },
}

LOGGING["loggers"] = {
    "django": {
        "handlers": ["console"],
        "level": "DEBUG",
        "propagate": True,
    },
    "django.server": {
        "handlers": ["django.server"],
        "level": LOG_LEVEL,
        "propagate": True,
    },
    "file": {
        "handlers": ["file"],
        "level": LOG_LEVEL,
        "propagate": True,
    },
}
