from django.db.models.signals import post_save,pre_save,post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from forum.models import ForumPost
from django.db.models import F
from django.contrib.contenttypes.models import ContentType
from base.models import UserNotificationSettings, NotificationSubject,NotificationSubscriber

@receiver(post_save, sender=ForumPost)
def forum_post_created(sender, instance, created, **kwargs):
    if created:
        content_type = ContentType.objects.get_for_model(sender)
        # Get or create the NotificationSubscriber for the ForumPost
        subscriber, created = NotificationSubscriber.objects.get_or_create(
            content_type=content_type,
            generic_object_id=instance.pk
        )

        subscriber.subscribers.add(instance.created_by)

  
@receiver(pre_save, sender=ForumPost)
def forum_post_updated(sender, instance, **kwargs):
        old_instance = sender.objects.filter(pk=instance.pk).annotate(
            old_title=F('title'),
            old_content=F('content')
        ).first()

        if old_instance:
            title_changed = old_instance.old_title != instance.title
            content_changed = old_instance.old_content != instance.content

            if title_changed:
                print(f"Title changed: {old_instance.old_title} -> {instance.title}")
            
            if content_changed:
                print(f"Content changed: {old_instance.old_content} -> {instance.content}")

@receiver(post_delete, sender=ForumPost)
def cleanup_notification_subscribers(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(sender)
    NotificationSubscriber.objects.filter(
        content_type=content_type,
        generic_object_id=instance.id
    ).delete()