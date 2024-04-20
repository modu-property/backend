from typing import Any, List, OrderedDict, Union
from django.db import models
from rest_framework.exceptions import ValidationError
from django.db.models import QuerySet
from rest_framework.utils.serializer_helpers import ReturnDict

from modu_property.utils.loggers import logger


def validate_data(
    serializer: Any = None,
    queryset: QuerySet = None,
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
) -> Union[List[OrderedDict[str, Union[int, str]]], ReturnDict, bool]:
    """
    model and data
    model과 dict data 있을 때?

    queryset
    dict data, model 없을 때 사용

    model and not data
    model serializer로 model 검증할 때

    data and not model
    model을 dict로 만들어서 model serializer 사용할 때
    """
    try:
        if model and data:
            _serializer = serializer(instance=model, data=data, many=many)
            _serializer.is_valid(raise_exception=True)
        elif queryset:
            _serializer = serializer(instance=queryset, many=many)
        elif model and not data:
            _serializer = serializer(instance=model, many=many)
        elif data and not model:
            _serializer = serializer(data=data, many=many)
            _serializer.is_valid(raise_exception=True)
        return _serializer.data
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
