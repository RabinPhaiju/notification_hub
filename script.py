import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_hub.settings')
django.setup()

from django.contrib.auth.models import User
from base.models import UserNotificationSettings,NotificationSubscriber,ForumNotificationSubject,Notification
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from forum.models import ForumPost

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

def add_subscriber_to_forum_1(user_name, model, object_id):
    user = User.objects.get(username=user_name)
    content_type = ContentType.objects.get_for_model(model)
    notificationSubs = NotificationSubscriber.objects.filter(
        content_type=content_type,
        generic_object_id=object_id
    ).first()
    
    if notificationSubs: # and user not in notificationSubs.subscribers.all():
        notificationSubs.subscribers.add(user)
    else: 
        print("No subscribers found.")

def remove_subscriber_from_forum_1(user_name, model, object_id):
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

def print_user_notification_settings(username):
    user = User.objects.filter(username=username)
    if user.exists():
        settings = UserNotificationSettings.objects.filter(user=user.first()).first()
        if settings:
            print('enabled:', settings.notifications_enabled)
            print('in_app:', settings.in_app)
            print('email:', settings.email)
            print('push_notification:', settings.push_notification)
        else:
            print("No settings found.")
    else:
        print("User not found.")

def notify_forum_subscribers_in_app(model, object_id, subject):
    forumPost = ForumPost.objects.get(id=object_id)
    if forumPost:
        content_type = ContentType.objects.get_for_model(model)

        subscribers_with_in_app_notify = UserNotificationSettings.objects.filter(
            Q(user__notification_subscribers__content_type=content_type),
            Q(user__notification_subscribers__generic_object_id=object_id),
            Q(subject=subject),
            Q(notifications_enabled = True) ,
            Q(in_app=True)
        ).select_related('user')

        for notification_setting in subscribers_with_in_app_notify:
            user = notification_setting.user
            print(user.username)
            Notification.objects.create(
                user=user,
                title=f"{forumPost.title} in {content_type.model}",
                description=f"{forumPost.title} has been posted in {content_type.model}.",
                category=subject
            )

def get_users_by_notification_type(model, object_id, subject):
    content_type = ContentType.objects.get_for_model(model)

    # Retrieve NotificationSubscribers for the specific object
    notification_subscribers = NotificationSubscriber.objects.filter(
        content_type=content_type,
        generic_object_id=object_id
    )

    # Get subscribed users in format of list
    subscribed_users = notification_subscribers.values_list('subscribers', flat=True)

    # Filter UserNotificationSettings based on subscribed users, content type, and subject
    user_settings = UserNotificationSettings.objects.filter(
        user__id__in=subscribed_users,
        content_type=content_type,
        subject=subject
    )

    # Separate users based on notification preferences
    email_users = user_settings.filter(email=True).values_list('user__email', flat=True)
    in_app_users = user_settings.filter(in_app=True).values_list('user__id', flat=True)
    push_notification_users = user_settings.filter(push_notification=True).values_list('user__id', flat=True)

    return {
        'email_users': list(email_users),
        'in_app_users': list(in_app_users),
        'push_notification_users': list(push_notification_users)
    }

def update_forum_post_title(model, object_id, title):
    forumPost = model.objects.get(id=object_id)
    forumPost.title = title
    forumPost.save()

def try_mixin(model, object_id):
    forumPost = model.objects.get(id=object_id)
    if forumPost:
        # forumPost.notify_subscribers(subject=ForumNotificationSubject.NEW_POST,type='email',
        #                 emailSubject="this is email subject",
        #                 emailBody="This is an important message body.",
        #                 )
        forumPost.notify_subscribers(subject=ForumNotificationSubject.NEW_POST,type='in_app',
                         title="you have a new notification",
                         description="This is an important message.",
                         )

# commands:
# create_user('sane', 'sane@example.com', 'password')
# print_users()
# print_notification_subscribers(ForumPost, 3)
# add_subscriber_to_forum_1('ram',ForumPost,3)
# remove_subscriber_from_forum_1('jane_smith',ForumPost,1)
# print_user_notification_settings('sijal')
# notify_forum_subscribers_in_app(ForumPost, 3, ForumNotificationSubject.NEW_POST)
# print(get_users_by_notification_type(ForumPost, 1, ForumNotificationSubject.NEW_POST))
# update_forum_post_title(ForumPost, 3, "post 3 updated")
# try_mixin(ForumPost, 8)