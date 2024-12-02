import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_hub.settings')
django.setup()

from django.contrib.auth.models import User
from base.models import UserNotificationSettings,NotificationSubscriber
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

def notify_forum_subscribers(model, object_id, subject):
    content_type = ContentType.objects.get_for_model(model)
    
    notification_subscribers = NotificationSubscriber.objects.filter(
        content_type=content_type,
        generic_object_id=object_id
    )

    # Get users who have email notifications enabled for the given subject
    subscribers_with_email_notify = (
        UserNotificationSettings.objects.filter(
            Q(user__in=notification_subscribers.values_list('subscribers', flat=True)),
            content_type=content_type,
            subject=subject,
            email=True
        )
        .select_related('user')  # Optimize query by fetching related user objects
    )

    for notification_setting in subscribers_with_email_notify:
        user = notification_setting.user
        print(f"Notify {user.username} via email for subject: {subject}")

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

# commands:
# create_user('jane_smith', 'jane@example.com', 'password456')
# print_users()
# add_subscriber_to_forum_1('jane_smith',ForumPost,1)
# remove_subscriber_from_forum_1('jane_smith',ForumPost,1)
# print_notification_subscribers(ForumPost, 1)
# print_user_notification_settings('rabinphaiju')
# notify_forum_subscribers(ForumPost, 1, 'new_post')
print(get_users_by_notification_type(ForumPost, 1, 'new_post'))