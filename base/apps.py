from django.apps import AppConfig


class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'

    def ready(self):
        import base.signals.signals
        import base.signals.forum_post_signals
        import base.signals.forum_reply_signals
