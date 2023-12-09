import logging
from typing import Union
from django.db import models
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

logger = logging.getLogger("django")


def validate_model(
    model: models.Model, data: dict, serializer: serializers.ModelSerializer
) -> Union[dict, bool]:
    try:
        serializer = serializer(instance=model, data=data)

        if not serializer.is_valid(raise_exception=True):
            return False

        serializer.initial_data
        serializer.validated_data
        data = serializer.data

        return data
    except ValueError as e:
        logger.info(f"validate_model ValueError e : {e}, data : {data}")
        return False
    except ValidationError as e:
        logger.info(f"validate_model ValidationError e : {e}, data : {data}")
        return False
    except Exception as e:
        logger.info(f"validate_model e : {e}")
        return False
