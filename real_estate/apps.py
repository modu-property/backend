from django.apps import AppConfig


class PropertyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "real_estate"

    # django 시작될 때 schema 등록하기 위함
    def ready(self):
        from modu_property.schema import CustomSimpleJWTScheme  # noqa: E402

        # 컨테이너 초기화용 import. real_estate/__init__.py엔 작성할 수 없음
        from real_estate.containers.service_container import (
            ServiceContainer,
        )  # noqa
        from real_estate.containers.search_container import (
            SearchContainer,
        )  # noqa
