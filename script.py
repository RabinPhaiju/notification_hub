import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_hub.settings')
django.setup()

from django.contrib.auth.models import User
from base.models import UserNotificationSetting,NotificationSubscriber,NotificationSubjectAll,NotificationAttribute
from django.contrib.contenttypes.models import ContentType
from forum.models import ForumPost,ForumPostReply,ForumNotificationSubject,ForumReplyNotificationSubject
from offer.models import Offer,OfferNotificationSubject
from base.utils import get_user_not_in_group_all,create_notification_settings,add_subscriber,remove_subscriber
from base.enums import NotifyTarget,NotificationTypes

def create_user(username, email, password):
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    user.save()

def print_user_notification_settings(username):
    user = User.objects.filter(username=username)
    if user.exists():
        settings = UserNotificationSetting.objects.filter(user=user.first());
        if settings.exists():
            for setting in settings:
                print(f'model: {setting.content_type.model}, subject: {setting.subject}, enabled: {setting.notifications_enabled}')
                print(f'email: {setting.email}, in_app: {setting.in_app}, push: {setting.push}')
        else:
            print("No settings found.")
    else:
        print("User not found.")

def print_notification_subscribers(model, object_id):
    content_type = ContentType.objects.get_for_model(model)
    notification_subscribers = NotificationSubscriber.objects.filter(
        content_type=content_type,
        generic_object_id=object_id
    ).first()
    
    if notification_subscribers:
        for subscriber in notification_subscribers.subscribers.all():
            print(subscriber.username)
    else:
        print("No subscribers found.")

def update_forum_post_title(model, object_id, title):
    forumPost = model.objects.get(id=object_id)
    forumPost.title = title
    forumPost.save()

def try_mixin(model, object_id, subject):
    record = model.objects.get(id=object_id)
    na = NotificationAttribute(
        title = 'test title',
        body = 'test body',
        # action_link = 'testing_link/1',
        # image_url='test_image.png',
        email_template = '<html>hi <a href="{{action_link}}">link</a></html>',
        # push_data = '{"action": "test"}',
    )
    if record:
        record.notify(
            subject=subject,
            types=[NotificationTypes.EMAIL],
            target = NotifyTarget.ALL,
            # notification_attribute=na
            )

# commands:
# create_user('shyam11', 'shyam11@example.com', 'password')
# print_user_notification_settings('ram')
# add_subscriber('ram',ForumPost,1)
# remove_subscriber('ram',ForumPost,1)
# print_notification_subscribers(ForumPost, 1)
# update_forum_post_title(ForumPost, 1, "post 1 updated")
# create_notification_settings(Offer)

# try_mixin(ForumPost, 1, ForumNotificationSubject.NEW_POST)
# try_mixin(ForumPostReply, 2, ForumReplyNotificationSubject.NEW_REPLY)
try_mixin(Offer, 1, OfferNotificationSubject.NEW_OFFER)
