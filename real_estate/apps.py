from django.apps import AppConfig


class PropertyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "real_estate"

    # django 시작될 때 schema 등록하기 위함
    def ready(self):
        from modu_property.schema import CustomSimpleJWTScheme  # noqa: E402
