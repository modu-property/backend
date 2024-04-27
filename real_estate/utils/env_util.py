import os


class EnvUtil:
    @staticmethod
    def not_test_env() -> bool:
        return os.getenv("SERVER_ENV") != "test"
