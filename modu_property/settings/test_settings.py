from dotenv import load_dotenv

load_dotenv(".env.test")

from .base_settings import *

DATABASES = {
    "default": {
        "ENGINE": ENGINE,
        "NAME": NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
        "TEST": {
            "NAME": f"test_{NAME}",
        },
    }
}

LOGGING["loggers"]["django"]["handlers"] = ["console", "file"]
