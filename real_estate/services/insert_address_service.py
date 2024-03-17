import os
from django.db import connections

from modu_property.utils.file import FileUtil


class InsertAddressService:
    def __init__(
        self,
    ) -> None:
        pass

    def get_file_path(self, file_name: str):
        dir_path = "tests/files"
        return os.path.join(os.getcwd(), dir_path, file_name)

    def execute(self) -> bool:

        connection = connections["default"]

        path: str = FileUtil.get_file_path(
            dir_name="tests/files", file_name="insert_regional_codes.sql"
        )

        # Read SQL commands from the file
        with open(path, "r") as file:
            sql_commands = file.read()

        # Split the SQL commands if there are multiple commands
        commands = sql_commands.split(";")  # [start : end + 1]

        # Execute each SQL command
        with connection.cursor() as cursor:
            for command in commands:
                if command.strip():
                    cursor.execute(command)
