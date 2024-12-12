from django.apps import AppConfig


class ForumConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'forum'

    def ready(self):
        import forum.signals.signals
        import forum.signals.forum_post_signals
        import forum.signals.forum_reply_signals
