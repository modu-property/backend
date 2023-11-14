from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme


class CustomSimpleJWTScheme(SimpleJWTScheme):
    target_class = "rest_framework_simplejwt.authentication.JWTAuthentication"  # full import path OR class ref
    name = "Authentication"
    priority = 1

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Bearer Authorization",
            "bearerFormat": "Bearer",
        }
