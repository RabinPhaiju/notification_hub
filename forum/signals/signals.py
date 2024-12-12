from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from forum.models import ForumPost,ForumPostReply
from django.contrib.contenttypes.models import ContentType
from base.models import UserNotificationSetting,ForumNotificationSubject,AuthNotificationSubject,NotificationSubjectAll,ForumReplyNotificationSubject,OfferNotificationSubject
from offer.models import Offer

def get_all_choices(NotificationSubject):
    return NotificationSubjectAll.choices + NotificationSubject.choices

# Create notification settings for new users -> ForumPost
@receiver(post_save, sender=User)
def create_notification_settings(sender, instance, created, **kwargs):
    current_user = User.objects.get(id=instance.id)
    if created and current_user.email: # and verified user
        # ForumPost
        content_type_forum = ContentType.objects.get_for_model(ForumPost)
        for subject in get_all_choices(ForumNotificationSubject):
            UserNotificationSetting.objects.create(
                user=instance,
                content_type=content_type_forum,
                subject=subject[0],
            )
        # ForumPostReply
        content_type_reply = ContentType.objects.get_for_model(ForumPostReply)
        for subject in get_all_choices(ForumReplyNotificationSubject):
            UserNotificationSetting.objects.create(
                user=instance,
                content_type=content_type_reply,
                subject=subject[0],
        )
        # Offer
        content_type_offer = ContentType.objects.get_for_model(Offer)
        for subject in get_all_choices(OfferNotificationSubject):
            UserNotificationSetting.objects.create(
                user=instance,
                content_type=content_type_offer,
                subject=subject[0],
        )
        # Auth
        content_type_auth = ContentType.objects.get_for_model(User)
        for subject in get_all_choices(AuthNotificationSubject):
            UserNotificationSetting.objects.create(
                user=instance,
                content_type=content_type_auth,
                subject=subject[0]
            )
