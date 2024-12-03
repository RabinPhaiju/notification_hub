from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from forum.models import ForumPost
from django.contrib.contenttypes.models import ContentType
from base.models import UserNotificationSettings, NotificationSubject

# Create notification settings for new users -> ForumPost
@receiver(post_save, sender=User)
def create_notification_settings(sender, instance, created, **kwargs):
    if created:
        content_type = ContentType.objects.get_for_model(ForumPost)
        for subject in NotificationSubject.choices:
            UserNotificationSettings.objects.create(
                user=instance,
                content_type=content_type,
                subject=subject[0]
            )
