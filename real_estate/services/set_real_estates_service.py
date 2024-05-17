from typing import Any, Dict, Optional, Union

from modu_property.utils.loggers import logger
from modu_property.utils.validator import validate_data
from real_estate.serializers import (
    GetRealEstatesOnSearchResponseSerializer,
    GetRegionsOnSearchResponseSerializer,
)


class SetRealEstatesService:
    def __init__(self, serializer, key) -> None:
        self.serializer: Union[
            GetRealEstatesOnSearchResponseSerializer,
            GetRegionsOnSearchResponseSerializer,
        ] = serializer
        self.key = key

    def update_result_with_data(
        self,
        result: Dict,
        data: list,
    ) -> Optional[bool]:
        if not data:
            result[self.key] = []
            return True

        _data: Any = validate_data(
            data=list(data),
            serializer=self.serializer,
            many=True,
        )
        if not _data:
            logger.error(
                f"update_result_with_data result : {result} _data : {data}"
            )
            return False

        result[self.key] = list(data)
        return True
