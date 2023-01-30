import datetime
import json
from pathlib import Path

import environ
import os

from celery.schedules import crontab

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Set the project base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def set_logging():
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
            "django.server": {
                "level": env("LOG_LEVEL"),
                "class": "logging.StreamHandler",
                "formatter": "django.server",
            },
            "file": {
                "level": env("LOG_LEVEL"),
                "filters": ["require_debug_true"],
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{BASE_DIR}/modu_property.log",
                "maxBytes": 1024 * 1024 * 5,  # 5 MB
                "backupCount": 5,
                "formatter": "django.server",
            },
        },
        "loggers": {
            "django.server": {
                "handlers": ["django.server"],
                "level": env("LOG_LEVEL"),
                "propagete": True,
            },
            "file": {
                "handlers": ["file"],
                "level": env("LOG_LEVEL"),
                "propagete": True,
            },
        },
    }


# FROM .env.* file
SERVER_ENV = os.environ.get("SERVER_ENV")
if SERVER_ENV == "dev":
    environ.Env.read_env(os.path.join(BASE_DIR, ".env.dev"))
elif SERVER_ENV == "stage":
    environ.Env.read_env(os.path.join(BASE_DIR, ".env.stage"))
elif SERVER_ENV == "prod":
    environ.Env.read_env(os.path.join(BASE_DIR, ".env.prod"))
elif SERVER_ENV == "test":
    environ.Env.read_env(os.path.join(BASE_DIR, ".env.test"))
else:
    environ.Env.read_env(os.path.join(BASE_DIR, ".env.local"))
LOGGING = set_logging()

# False if not in os.environ because of casting above
DEBUG = env("DEBUG")

# Raises Django's ImproperlyConfigured
# exception if SECRET_KEY not in os.environ
SECRET_KEY = env("SECRET_KEY")

CELERY_BROKER_URL = env("CELERY_BROKER_URL")
ENGINE = env("DB_ENGINE")
NAME = env("DB_NAME")
USER = env("USER")
DB_PASSWORD = env("DB_PASSWORD")
DB_HOST = env("DB_HOST")
DB_PORT = env("DB_PORT")
NAVER_NEWS_API_CLIENT_ID = env("NAVER_NEWS_API_CLIENT_ID")
NAVER_NEWS_API_CLIENT_SECRET = env("NAVER_NEWS_API_CLIENT_SECRET")
DJANGO_ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS", default="").split(" ")
ALLOWED_HOSTS = DJANGO_ALLOWED_HOSTS
POSTGRES_USER = env("POSTGRES_USER", default="")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "app",
    "accounts",
    "modu_property",
    "django_celery_beat",
    "rest_framework"
    # "rest_framework_simplejwt",
]

# TODO : rest_framework_simplejwt 설정 필요 없으면 제거
# REST_FRAMEWORK = {
#     "DEFAULT_AUTHENTICATION_CLASSES": (
#         "rest_framework_simplejwt.authentication.JWTAuthentication",
#     )
# }

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

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


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": ENGINE,
        "NAME": NAME,
        "USER": USER,
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
    "AUTH_HEADER_TYPES": ("JWT",),
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
    "collect_property_news_every_5_minutes": {
        "task": "modu_property.tasks.collect_property_news_task",
        "schedule": crontab(minute="*/5"),
        "kwargs": {"display": 100},
    },
}
