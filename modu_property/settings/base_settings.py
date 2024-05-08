import os
import datetime
import socket

from celery.schedules import crontab

from modu_property.utils.file import FileUtil
from modu_property.utils.loggers import logger, file_logger

LOG_LEVEL = os.getenv("LOG_LEVEL")


log_file = FileUtil.get_file_path(
    dir_name="modu_property/logs/", file_name="modu_property.log"
)

logger.info(f"log file : {log_file}")


def set_logging():
    log_file = FileUtil.get_file_path(
        dir_name="modu_property/logs/", file_name="modu_property.log"
    )
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "require_debug_false": {
                "()": "django.utils.log.RequireDebugFalse",
            },
            "require_debug_true": {
                "()": "django.utils.log.RequireDebugTrue",
            },
        },
        "formatters": {
            "django.server": {
                "()": "django.utils.log.ServerFormatter",
                "format": "{asctime} {filename}:{funcName}:{lineno} [{levelname}] {message}",
                "style": "{",
            },
        },
        "handlers": {
            "console": {
                "level": LOG_LEVEL,
                "filters": ["require_debug_false"],
                "class": "logging.StreamHandler",
            },
            "django.server": {  # python manage.py runserver로 작동하는 개발 서버에서만 사용하는 핸들러로 콘솔에 로그를 출력
                "level": LOG_LEVEL,
                "class": "logging.StreamHandler",
                "formatter": "django.server",
            },
            "file": {
                "level": LOG_LEVEL,
                "filters": ["require_debug_false"],
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_file,
                "maxBytes": 1024 * 1024 * 50,  # 50 MB
                "backupCount": 5,
                "formatter": "django.server",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": "INFO",
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
        },
    }


SERVER_ENV = os.environ.get("SERVER_ENV")

LOGGING = set_logging()

DEBUG = os.getenv("DEBUG")

LOG_LEVEL = os.getenv("LOG_LEVEL")

# Raises Django's ImproperlyConfigured
# exception if SECRET_KEY not in os.environ
SECRET_KEY = os.getenv("SECRET_KEY")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
ENGINE = os.getenv("DB_ENGINE")
NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DJANGO_ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", default="").split(" ")
ALLOWED_HOSTS = DJANGO_ALLOWED_HOSTS
DB_USER = os.getenv("DB_USER", default="")

# Application definition

INSTALLED_APPS = [
    "debug_toolbar",
    "drf_spectacular",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "real_estate",
    "accounts",
    "modu_property",
    "django_celery_beat",
    "rest_framework",
    "rest_framework_simplejwt",
    "django.contrib.gis",
    "corsheaders",
]

# TODO : rest_framework_simplejwt 설정 필요 없으면 제거
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # "rest_framework_simplejwt.authentication.JWTAuthentication"
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # django debug toolbar css 해결 용
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ] + MIDDLEWARE

ROOT_URLCONF = "modu_property.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "modu_property.wsgi.application"

APPEND_SLASH = False

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": ENGINE,
        "NAME": NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
    },
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(hours=6),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=14),
    "SIGNING_KEY": SECRET_KEY,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

AUTH_USER_MODEL = "accounts.User"

# Celery Configuration Options
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = CELERY_BROKER_URL
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_BEAT_SCHEDULE = {
    "collect_deal_price_of_real_estate_every_hour_from_9_to_18": {
        "task": "modu_property.tasks.collect_deal_price_of_real_estate_task",
        "schedule": crontab(hour="9-18"),
        "kwargs": {"sido": "서울특별시"},
    },
}


from glob import glob

_libgdal = glob("/usr/lib/libgdal.so.*")
_libgeos_c = glob("/usr/lib/libgeos_c.so.*")
GDAL_LIBRARY_PATH = ""
GEOS_LIBRARY_PATH = ""
if _libgdal:
    GDAL_LIBRARY_PATH = _libgdal[0]
if _libgeos_c:
    GEOS_LIBRARY_PATH = _libgeos_c[0]

SPECTACULAR_SETTINGS = {
    "TITLE": "모두의 부동산 API",
    "DESCRIPTION": "부동산 계산기. 시세. 검색. 매칭",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}


if DEBUG:
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [".".join(ip.split(".")[:-1]) + ".1" for ip in ips]
