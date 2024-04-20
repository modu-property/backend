import os
from django.db import connections

from modu_property.utils.file import FileUtil


class InsertRegionsService:
    def insert_regions(self) -> None:
        connection = connections["default"]

        path: str = FileUtil.get_file_path(
            dir_name="tests/files", file_name="insert_regional_codes.sql"
        )

        queries = self.get_queries(path)

        self.execute_queries(connection, queries)

    @staticmethod
    def get_file_path(file_name: str) -> str:
        dir_path = "tests/files"
        return os.path.join(os.getcwd(), dir_path, file_name)

    @staticmethod
    def get_queries(path):
        with open(path, "r") as file:
            return file.read().split(";")

    @staticmethod
    def execute_queries(connection, queries):
        with connection.cursor() as cursor:
            for query in queries:
                if query.strip():
                    cursor.execute(query)
