"""
manticore_{SERVER_ENV}.conf 파일에 .env의 환경 변수를 replace해주는 스크립트
"""
import os
from dotenv import load_dotenv
from shutil import copyfile

SERVER_ENV = os.getenv("SERVER_ENV")
load_dotenv(verbose=True, dotenv_path=f".env.{SERVER_ENV}")

# Get the secret from .env
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def read_file():
    with open(f"./manticore/manticore_{SERVER_ENV}.conf", "r") as f:
        config_contents = f.read()
    return config_contents


def open_and_modify_file(config_contents):
    config_contents = config_contents.replace("DB_HOST", DB_HOST)
    config_contents = config_contents.replace("DB_PORT", DB_PORT)
    config_contents = config_contents.replace("DB_USER", DB_USER)
    config_contents = config_contents.replace("DB_PASSWORD", DB_PASSWORD)
    config_contents = config_contents.replace("DB_NAME", DB_NAME)

    write_env(config_contents)

    copyfile(f"./manticore/manticore_{SERVER_ENV}.conf", "./manticore/manticore.conf")


def write_env(config_contents):
    with open(f"./manticore/manticore_{SERVER_ENV}.conf", "w") as f:
        f.write(config_contents)


def restore_original_file():
    copyfile(
        "./manticore/manticore_tmp.conf", f"./manticore/manticore_{SERVER_ENV}.conf"
    )


def replace_manticore_conf():
    copyfile(
        f"./manticore/manticore_{SERVER_ENV}.conf", "./manticore/manticore_tmp.conf"
    )
    config_contents = read_file()
    open_and_modify_file(config_contents)
    restore_original_file()
    os.remove("./manticore/manticore_tmp.conf")
