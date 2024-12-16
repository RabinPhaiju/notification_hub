from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from .models import UserNotificationSetting,NotificationSubjectAll
from .helpers import sent_mail,sent_in_app,sent_push,format_notification_attribute,get_notification_type_attributes_email,get_notification_type_attributes_users
from .utils import convert_notifications_to_email_messages
from .enums import NotifyTarget,NotificationTypes

class NotificationModelMixin:
    def notify(self,subject,types,target,notification_attribute=None):
        default_types = [NotificationTypes.NOTIFICATIONS_ENABLED]
        types = list(set(default_types+types))

        if target == NotifyTarget.NEWSLETTER_EMAIL:
            # get user emails
            user_group = ['test1@email.com']
        else:
            # Get user notification settings from query
            user_settings_query = get_user_settings_query(self,subject,target)
            user_settings = UserNotificationSetting.objects.filter(*user_settings_query).select_related('user')

            # create and get user_group with settings types
            user_group = get_user_group(user_settings,types)

            # Create notification settings
            create_notification_settings_subject(self,user_group,subject)

        # Create notifications
        create_notification_attributes(self,user_group,subject,types,target,notification_attribute)

def get_user_settings_query(obj,subject,target):
    content_type = ContentType.objects.get_for_model(obj.__class__)
    query = [
        Q(content_type=content_type),
        Q(subject__in=[subject,NotificationSubjectAll.ALL]),
    ]
    if target == NotifyTarget.SUBSCRIBERS or target == NotifyTarget.NEWSLETTER:
        query.extend([
            Q(user__notification_subscribers__content_type=content_type),
            Q(user__notification_subscribers__generic_object_id=obj.id),
        ])
    return query

def get_user_group(subscribers_settings,types):
    user_group = dict()
    for subscriber_setting in subscribers_settings:
        if subscriber_setting.user not in user_group:
            user_group[subscriber_setting.user] = {
                subscriber_setting.subject: {**{type_key: getattr(subscriber_setting, type_key.value) for type_key in types},}
                }
        user_group[subscriber_setting.user][subscriber_setting.subject] = {
                    **{type_key: getattr(subscriber_setting, type_key.value) for type_key in types},
        }

    return user_group

def create_notification_settings_subject(obj,user_group,subject):
    users_not_with_group = [u for u, details in user_group.items() if not details.get(subject)]
    if users_not_with_group:
        content_type = ContentType.objects.get_for_model(obj.__class__)
        settings_to_create = [
            UserNotificationSetting(user=user, subject=subject, content_type=content_type)
            for user in users_not_with_group
        ]
        instances = UserNotificationSetting.objects.bulk_create(settings_to_create)
        # Bulk create user notification settings -- but bulk create dont work signals (post_save,pre_save,post_delete)
        # Manually send the post_save signal
        # for instance in instances:
            # post_save.send(sender=UserNotificationSetting, instance=instance, created=True)

def create_notification_attributes(obj,user_group,subject,types,target,notification_attribute):
    # format notification attribute
    na = format_notification_attribute(obj,subject,notification_attribute)
    
    if target == NotifyTarget.NEWSLETTER_EMAIL:
        notification_type_attributes = get_notification_type_attributes_email(user_group,obj,na)
    else:
        notification_type_attributes = get_notification_type_attributes_users(user_group,subject,types,obj,na)
        # sent in_app
        in_app_notifications = notification_type_attributes[NotificationTypes.IN_APP]
        sent_in_app(in_app_notifications)

        # sent push
        push_notifications = notification_type_attributes[NotificationTypes.PUSH]
        sent_push(push_notifications)
   
    # sent email
    email_notifications = convert_notifications_to_email_messages(notification_type_attributes[NotificationTypes.EMAIL])
    sent_mail(email_notifications)

