from typing import Any, Union


class ServiceResultDto:
    def __init__(
        self,
        data: Union[dict, list, None, Any] = None,
        message: str = "OK",
        status_code: int = 200,
    ) -> None:
        self.data = data
        self.message = message
        self.status_code: int = status_code
