from abc import ABC, abstractmethod

from rest_framework import status


class ExceptionInterface(Exception, ABC):
    @abstractmethod
    def __init__(self, message: str = None, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class NotFoundException(ExceptionInterface):
    def __init__(self, message: str = None, status_code: int = None):
        super().__init__(message, status_code)
        self.status_code = status.HTTP_404_NOT_FOUND


class SearchAndUpdateRealEstatesException(ExceptionInterface):
    def __init__(self, message: str = None, status_code: int = None):
        super().__init__(message, status_code)
        self.status_code = status.HTTP_400_BAD_REQUEST
