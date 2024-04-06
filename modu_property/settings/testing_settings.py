from dotenv import load_dotenv

load_dotenv(".env.testing")

from .base_settings import *
from modu_property.utils.loggers import logger


log_file = FileUtil.get_file_path(
    dir_name="modu_property/logs/", file_name="modu_property.log"
)
logger.info(f"log file : {log_file}")

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
        "filename": log_file,
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
