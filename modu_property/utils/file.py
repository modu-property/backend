import os


class FileUtil:
    @staticmethod
    def get_file_path(dir_name: str, file_name: str):
        dir_path = f"{dir_name}/"
        return os.path.join(os.getcwd(), dir_path, file_name)
