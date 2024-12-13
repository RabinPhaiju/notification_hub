from django.apps import AppConfig
from .registry import register_subject_choices

class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'

    def ready(self):
        from .models import NotificationSubjectAll
        register_subject_choices(NotificationSubjectAll.choices)
