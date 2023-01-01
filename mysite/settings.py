import datetime
from pathlib import Path

import environ
import os

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
                "format": "{asctime} [{levelname}] {message} {filename}:{lineno}",
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
                "filename": f"{BASE_DIR}/mysite.log",
                "maxBytes": 1024 * 1024 * 5,  # 5 MB
                "backupCount": 5,
                "formatter": "django.server",
            },
        },
        "loggers": {
            "django.server": {
                "handlers": ["django.server", "file"],
                "level": env("LOG_LEVEL"),
                "propagete": True,
            },
        },
    }


# FROM .env.* file
server_env = os.environ.get("server_env")
if server_env == "dev":
    environ.Env.read_env(os.path.join(BASE_DIR, ".env.dev"))
elif server_env == "stage":
    environ.Env.read_env(os.path.join(BASE_DIR, ".env.stage"))
elif server_env == "prod":
    environ.Env.read_env(os.path.join(BASE_DIR, ".env.prod"))
elif server_env == "test":
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

ALLOWED_HOSTS = []

ENGINE = env("DB_ENGINE")
NAME = env("DB_NAME")
USER = env("USER")
PASSWORD = env("PASSWORD")
HOST = env("HOST")
PORT = env("PORT")

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
    "mysite",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mysite.urls"

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

WSGI_APPLICATION = "mysite.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": ENGINE,
        "NAME": NAME,
        "USER": USER,
        "PASSWORD": PASSWORD,
        "HOST": HOST,
        "PORT": PORT,
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
