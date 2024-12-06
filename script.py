import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_hub.settings')
django.setup()

from django.contrib.auth.models import User
from base.models import UserNotificationSetting,NotificationSubscriber,ForumNotificationSubject
from django.contrib.contenttypes.models import ContentType
from forum.models import ForumPost
from base.utils import Utils

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

def notify_subscribers(model, object_id, subject, types=['in_app','email']):
    default_types = ['notifications_enabled']
    types = list(set(default_types+types))
    record = model.objects.get(id=object_id)
    if record:
        user_group = Utils.get_user_group_settings(model,object_id, subject, types)

        for user in user_group:
            # check if user have 'subject' settings
            if not user_group[user].get(subject,False):
                # create user notification subject
                uns = UserNotificationSetting.objects.create(
                    user=user,subject=subject,
                    content_type=ContentType.objects.get_for_model(model),
                )
                user_group[user][subject] = {'notifications_enabled':uns.notifications_enabled,'in_app':uns.in_app,'email':uns.email,'push_notification':uns.push_notification}
            
            if user_group[user]['all']['notifications_enabled'] and user_group[user][subject]['notifications_enabled']:
                if 'in_app' in types and user_group[user]['all']['in_app'] and user_group[user][subject]['in_app']:
                    print('in_app',user,user_group[user])
                if 'email' in types and user_group[user]['all']['email'] and user_group[user][subject]['email']:
                    print('email',user,user_group[user])   
                if 'push_notification' in types and user_group[user]['all']['push_notification'] and user_group[user][subject]['push_notification']: 
                    print('push_notification',user,user_group[user])

def try_mixin(model, object_id, subject):
    record = model.objects.get(id=object_id)
    if record:
        record.notify_subscribers(subject=subject,types=['in_app','email'],
                         title="you have a new notification",
                         description="This is an important message.",
                         )

# commands:
# create_user('shyam', 'shyam@example.com', 'password')
# print_users()
# print_user_notification_settings('ram')
# add_subscriber_to_forum('ram',ForumPost,1)
# remove_subscriber_from_forum('ram',ForumPost,1)
# print_notification_subscribers(ForumPost, 1)
# update_forum_post_title(ForumPost, 1, "post 1 updated")
notify_subscribers(ForumPost, 1, ForumNotificationSubject.NEW_POST)
# try_mixin(ForumPost, 1, ForumNotificationSubject.NEW_POST)