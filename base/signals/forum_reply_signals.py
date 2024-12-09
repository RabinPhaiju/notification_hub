from django.db.models.signals import post_save,pre_save,post_delete
from django.dispatch import receiver
from forum.models import ForumPostReply,ForumPost
from django.db.models import F
from django.contrib.contenttypes.models import ContentType
from base.models import NotificationSubscriber

@receiver(post_save, sender=ForumPostReply)
def forum_post_reply_created(sender, instance, created, **kwargs):
    if created:
        # ForumPostReply
        content_type = ContentType.objects.get_for_model(sender)
        subscriber, created = NotificationSubscriber.objects.get_or_create(
            content_type=content_type,
            generic_object_id=instance.pk
        )
        subscriber.subscribers.add(instance.created_by)

        # ForumPost
        content_type = ContentType.objects.get_for_model(ForumPost)
        subscriber, created = NotificationSubscriber.objects.get_or_create(
            content_type=content_type,
            generic_object_id=instance.post.pk
        )
        subscriber.subscribers.add(instance.created_by)

  
@receiver(pre_save, sender=ForumPostReply)
def forum_post_reply_updated(sender, instance, **kwargs):
        old_instance = sender.objects.filter(pk=instance.pk).annotate(
            old_content=F('content')
        ).first()

        if old_instance:
            content_changed = old_instance.old_content != instance.content

            if content_changed:
                print(f"Content changed: {old_instance.old_content} -> {instance.content}")

@receiver(post_delete, sender=ForumPostReply)
def cleanup_notification_subscribers(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(sender)
    NotificationSubscriber.objects.filter(
        content_type=content_type,
        generic_object_id=instance.id
    ).delete()