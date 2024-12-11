import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_hub.settings')
django.setup()

from django.contrib.auth.models import User
from base.models import UserNotificationSetting,NotificationSubscriber,ForumNotificationSubject,NotificationSubjectAll,ForumReplyNotificationSubject,OfferNotificationSubject,NotificationAttribute
from django.contrib.contenttypes.models import ContentType
from forum.models import ForumPost,ForumPostReply
from offer.models import Offer
from utils import get_user_not_in_group_all,get_model_attributes

def create_user(username, email, password):
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    user.save()

def print_users():
    users = User.objects.all()
    for user in users:
        print(user.username)

def print_user_notification_settings(username):
    user = User.objects.filter(username=username)
    if user.exists():
        settings = UserNotificationSetting.objects.filter(user=user.first());
        if settings.exists():
            for setting in settings:
                print(f'model: {setting.content_type.model}, subject: {setting.subject}, enabled: {setting.notifications_enabled}')
                print(f'email: {setting.email}, in_app: {setting.in_app}, push_notification: {setting.push_notification}')
                print('---------------')
        else:
            print("No settings found.")
    else:
        print("User not found.")

def add_subscriber_to_forum(user_name, model, object_id):
    user = User.objects.get(username=user_name)
    # to add users to subscribers, add directly no need to check the user's settings.
    content_type = ContentType.objects.get_for_model(model)
    notificationSubs = NotificationSubscriber.objects.filter(
        content_type=content_type,
        generic_object_id=object_id
    ).first()
    
    if notificationSubs: # and user not in notificationSubs.subscribers.all():
        notificationSubs.subscribers.add(user)
    else: 
        print("No subscribers found.")

def remove_subscriber_from_forum(user_name, model, object_id):
    # directly remove user from subscribers
    user = User.objects.get(username=user_name)
    content_type = ContentType.objects.get_for_model(model)
    notificationSubs = NotificationSubscriber.objects.filter(
        content_type=content_type,
        generic_object_id=object_id
    ).first()
    
    if notificationSubs:
        notificationSubs.subscribers.remove(user)
    else: 
        print("No subscribers found.")

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

def notify_subscribers(model, object_id, subject, types=['in_app','email','push_notification']):
    default_types = ['notifications_enabled']
    types = list(set(default_types+types))
    record = model.objects.get(id=object_id)
    if record:
        user_group = get_user_group_settings(model,object_id, subject, types)

        # Bulk create user notification settings -- but bulk create dont work signals (post_save,pre_save,post_delete)
        users_not_with_group = [u for u, details in user_group.items() if not details.get(subject)]
        settings_to_create = [
            UserNotificationSetting( user=user, subject=subject, content_type=ContentType.objects.get_for_model(model))
            for user in users_not_with_group
        ]
        UserNotificationSetting.objects.bulk_create(settings_to_create)

        for user in user_group:
            # check if user have 'subject' settings
            if not user_group[user].get(subject,False):
                # create user notification subject individually
                # uns = UserNotificationSetting.objects.create(
                #     user=user,subject=subject,content_type=ContentType.objects.get_for_model(model),
                # )
                user_group[user][subject.lower()] = {'notifications_enabled':True,'in_app':True,'email':True,'push_notification':True}
            
            if user_group[user][NotificationSubjectAll.ALL]['notifications_enabled'] and user_group[user][subject]['notifications_enabled']:
                if 'in_app' in types and\
                user_group[user][NotificationSubjectAll.ALL]['in_app'] and\
                user_group[user][subject]['in_app']:
                    print('in_app--',user,user_group[user])
                if 'email' in types and\
                user_group[user][NotificationSubjectAll.ALL]['email'] and\
                user_group[user][subject]['email']:
                    print('email--',user,user_group[user])   
                if 'push_notification' in types and\
                user_group[user][NotificationSubjectAll.ALL]['push_notification'] and\
                user_group[user][subject]['push_notification']:
                    print('push_notification--',user,user_group[user])

def try_mixin(model, object_id, subject):
    record = model.objects.get(id=object_id)
    na = NotificationAttribute(
        title = 'test title',
        body = 'test body',
        email_html = '<html>hi</html>',
        push_data = '{"action": "test"}',
    )
    if record:
        record.notify(
            subject=subject,
            types=['email','push_notification','in_app'],
            only_subs=False,
            # notification_attribute=na
            )

def create_notification_settings(model, subjects=[NotificationSubjectAll.ALL]):
    users_to_create = get_user_not_in_group_all(model)
    if users_to_create.exists():
        content_type = ContentType.objects.get_for_model(model)
        notification_to_create = [
            UserNotificationSetting(user=user, subject=subject, content_type=content_type)
            for user in users_to_create
            for subject in subjects
        ]
        UserNotificationSetting.objects.bulk_create(notification_to_create)
 
# commands:
# create_user('ram', 'ram@example.com', 'password')
# print_users()
# print_user_notification_settings('ram')
# add_subscriber_to_forum('ram',ForumPost,1)
# remove_subscriber_from_forum('ram',ForumPost,1)
# print_notification_subscribers(ForumPost, 1)
# update_forum_post_title(ForumPost, 1, "post 1 updated")
# notify_subscribers(ForumPost, 1, ForumNotificationSubject.NEW_POST,types=['in_app','email'])
try_mixin(ForumPost, 1, ForumNotificationSubject.NEW_POST)
# notify_subscribers(ForumPostReply, 2, ForumReplyNotificationSubject.NEW_REPLY)
# try_mixin(ForumPostReply, 2, ForumReplyNotificationSubject.NEW_REPLY)

# create_notification_settings(Offer)

# Offer
# try_mixin(Offer, 1, OfferNotificationSubject.NEW_OFFER)
