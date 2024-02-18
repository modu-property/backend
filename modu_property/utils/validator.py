from typing import Any, Union
from django.db import models
from rest_framework.exceptions import ValidationError
from django.db.models import QuerySet

from modu_property.utils.loggers import logger


def validate_data(
    serializer: Any = None,
    data: Union[
        list[dict],
        dict,
        bool,
        QuerySet,
        models.Model,
        None,
    ] = None,
    model: Union[models.Model, None] = None,
    many: bool = False,
) -> Union[dict, bool, Any]:
    """
    serializer에 queryset 넣는 경우 model에 queryset 할당
    serializer에 queryset이 아닌 커스텀 데이터 넣는 경우 data에 dict 할당
    """
    try:
        _data = None
        if model and not data:
            _serializer = serializer(instance=model, many=many)
            _data = _serializer.data
        elif model or data:
            _serializer = serializer(instance=model, data=data, many=many)
            _serializer.is_valid(raise_exception=True)
            _serializer.initial_data
            _serializer.validated_data
            _data = _serializer.data

        return _data
    except ValueError as e:
        logger.error(
            f"validate_model ValueError e : {e}, serializer : {serializer}, data : {data}, model : {model}, many : {many}"
        )
        return False
    except ValidationError as e:
        logger.error(
            f"validate_model ValidationError e : {e}, serializer : {serializer}, data : {data}, model : {model}, many : {many}"
        )
        return False
    except Exception as e:
        logger.error(
            f"validate_model e : {e}, serializer : {serializer}, data : {data}, model : {model}, many : {many}"
        )
        return False
