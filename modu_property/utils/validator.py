from typing import Any, Union
from django.db import models
from rest_framework.exceptions import ValidationError

from modu_property.utils.loggers import logger


def validate_data(
    serializer: Any = None,
    data: Union[list[dict], dict, bool, models.Model, None] = None,
    model: Union[models.Model, None] = None,
    many: bool = False,
) -> Union[dict, bool, Any]:
    try:
        _data = None
        if model and not data:
            serializer = serializer(instance=model, many=many)
            _data = serializer.data
        elif model or data:
            serializer = serializer(instance=model, data=data, many=many)
            if not serializer.is_valid(raise_exception=True):
                return False

            serializer.initial_data
            serializer.validated_data
            _data = serializer.data

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
