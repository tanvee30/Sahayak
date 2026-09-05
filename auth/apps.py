from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "auth"
    label = "sahayak_auth"   # avoids clashing with django.contrib.auth's own "auth" label
    verbose_name = "Sahayak Auth"