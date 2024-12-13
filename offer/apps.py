from django.apps import AppConfig
from base.registry import register_subject_choices,get_subject_choices

class OfferConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'offer'

    def ready(self):
        from .models import OfferNotificationSubject
        from base.models import UserNotificationSetting
        # Register offer-specific subject choices
        register_subject_choices(OfferNotificationSubject.choices)
        # Dynamically set the model field choices
        UserNotificationSetting._meta.get_field('subject').choices = get_subject_choices()