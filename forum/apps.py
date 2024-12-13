from django.apps import AppConfig
from base.registry import register_subject_choices,get_subject_choices

class ForumConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'forum'

    def ready(self):
        import forum.signals.signals
        import forum.signals.forum_post_signals
        import forum.signals.forum_reply_signals
        from .models import ForumNotificationSubject,ForumReplyNotificationSubject
        from base.models import UserNotificationSetting
        # Register offer-specific subject choices
        register_subject_choices(
            ForumNotificationSubject.choices+ForumReplyNotificationSubject.choices
            )
        # Dynamically set the model field choices
        UserNotificationSetting._meta.get_field('subject').choices = get_subject_choices()