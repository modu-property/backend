class MetaException(Exception):
    def __init__(self, message: str = None, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class NotFoundException(MetaException):
    pass


class SearchAndUpdateRealEstatesException(MetaException):
    pass
