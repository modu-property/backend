from typing import Any, Union
from django.db import models
from rest_framework.exceptions import ValidationError

from modu_property.utils.loggers import logger


def validate_model(
    data: Union[list[dict], bool],
    serializer,
    model: Union[models.Model, None] = None,
    many: bool = False,
) -> Union[dict, bool, Any]:
    try:
        if model:
            serializer = serializer(instance=model, data=data, many=many)
        else:
            serializer = serializer(data=data, many=many)

        if not serializer.is_valid(raise_exception=True):
            return False

        serializer.initial_data
        serializer.validated_data
        data = serializer.data

        return data
    except ValueError as e:
        logger.error(f"validate_model ValueError e : {e}, data : {data}")
        return False
    except ValidationError as e:
        logger.error(f"validate_model ValidationError e : {e}, data : {data}")
        return False
    except Exception as e:
        logger.error(f"validate_model e : {e}")
        return False
