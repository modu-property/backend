from typing import Any, Dict, Optional, Union

from modu_property.utils.loggers import logger
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

    def update_result_with_real_estates(
        self,
        result: Dict,
        real_estates: list,
    ) -> Optional[bool]:
        if not real_estates:
            result[self.key] = []
            return True

        _data = self.serializer(data=list(real_estates), many=True)
        if not _data:
            logger.error(
                f"update_result_with_data result : {result} _data : {real_estates}"
            )
            return False

        result[self.key] = list(real_estates)
        return True
