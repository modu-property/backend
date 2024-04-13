import os
from django.db import connections

from modu_property.utils.file import FileUtil


class InsertRegionsService:
    def __init__(
        self,
    ) -> None:
        pass

    def insert_regions(self) -> None:
        connection = connections["default"]

        path: str = FileUtil.get_file_path(
            dir_name="tests/files", file_name="insert_regional_codes.sql"
        )

        queries = self.get_queries(path)

        self.execute_queries(connection, queries)

    def get_file_path(self, file_name: str) -> str:
        dir_path = "tests/files"
        return os.path.join(os.getcwd(), dir_path, file_name)

    def get_queries(self, path):
        with open(path, "r") as file:
            return file.read().split(";")

    def execute_queries(self, connection, queries):
        with connection.cursor() as cursor:
            for query in queries:
                if query.strip():
                    cursor.execute(query)
