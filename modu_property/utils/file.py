import os


class FileUtil:
    @staticmethod
    def get_file_path(dir_name: str, file_name: str):
        dir_path = f"{dir_name}"
        path = os.path.join(os.getcwd(), dir_path, file_name)
        print(f"dir_name : {dir_name}, file_name : {file_name}, path : {path}")

        return path
