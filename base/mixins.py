from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
import json
from .models import UserNotificationSetting,NotificationSubjectAll,NotificationAttributeAdapter
from .helpers import sent_email_notification,sent_in_app_notification,sent_push_notification,format_notification_attribute
from .enums import NotifyTarget,NotificationTypes
from .utils import format_message

class NotificationModelMixin:
    def notify(self, subject, types,target,notification_attribute=None):
        default_types = [NotificationTypes.NOTIFICATIONS_ENABLED]
        types = list(set(default_types+types))

        if target == NotifyTarget.NEWSLETTER_EMAIL:
            # get user emails
            user_group = ['test1@email.com']
        else:
            # Get user notification settings from query
            user_settings = get_user_settings(self,subject,target)

            # create user_group with settings types
            user_group = create_user_group(user_settings,types)

            # Create notification settings
            create_notification_settings_subject(self,user_group,subject)

        # Create notifications
        create_notification_attributes(self,user_group,subject,types,target,notification_attribute)

def get_user_settings(obj,subject,target):
    content_type = ContentType.objects.get_for_model(obj.__class__)
    query = [
        Q(content_type=content_type),
        Q(subject__in=[subject,NotificationSubjectAll.ALL]),
    ]
    if target == NotifyTarget.SUBSCRIBERS:
        query.extend([
            Q(user__notification_subscribers__content_type=content_type),
            Q(user__notification_subscribers__generic_object_id=obj.id),
        ])
    return UserNotificationSetting.objects.filter(*query).select_related('user')

def create_user_group(subscribers_settings,types):
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
        notification_type_attributes = create_notification_type_attributes_email(user_group,obj,na)
    else:
        notification_type_attributes = create_notification_type_attributes_users(user_group,subject,types,obj,na)
        # sent in_app and push notification
        sent_in_app_notification(notification_type_attributes[NotificationTypes.IN_APP])
        sent_push_notification(notification_type_attributes[NotificationTypes.PUSH])
   
    # sent email notification
    sent_email_notification(notification_type_attributes[NotificationTypes.EMAIL])

def create_notification_type_attributes_users(user_group,subject,types,obj,na):
    in_app_attributes = []
    email_attributes = []
    push_attributes = []
    for user in user_group:
        # check if user have 'subject' settings
        if not user_group[user].get(subject,False):
            user_group[user][subject.lower()] = {
                NotificationTypes.NOTIFICATIONS_ENABLED:True,
                NotificationTypes.IN_APP:True,
                NotificationTypes.EMAIL:True,
                NotificationTypes.PUSH:True
                }

        if user_group[user][NotificationSubjectAll.ALL][NotificationTypes.NOTIFICATIONS_ENABLED] and user_group[user][subject][NotificationTypes.NOTIFICATIONS_ENABLED]:
            if NotificationTypes.IN_APP in types and\
            user_group[user][NotificationSubjectAll.ALL][NotificationTypes.IN_APP] and\
            user_group[user][subject][NotificationTypes.IN_APP]:
                naa = NotificationAttributeAdapter(user=user,type=NotificationTypes.IN_APP,attribute=na)
                in_app_attributes.append(naa)

            if NotificationTypes.EMAIL in types and\
            user_group[user][NotificationSubjectAll.ALL][NotificationTypes.EMAIL] and\
            user_group[user][subject][NotificationTypes.EMAIL]:
                na.email_template = format_message(na.email_template,{'obj':obj,'user':user,'action_link':na.action_link})
                na.email_attachment_url=na.image_url
                naa = NotificationAttributeAdapter(user_email=user.email,type=NotificationTypes.EMAIL,attribute=na)
                email_attributes.append(naa)

            if NotificationTypes.PUSH in types and\
            user_group[user][NotificationSubjectAll.ALL][NotificationTypes.PUSH] and\
            user_group[user][subject][NotificationTypes.PUSH]: 
                json_data = json.loads(na.push_data or '{}') # can be moved above loop
                json_data['id'] = str(obj.id)
                json_data['title'] = na.title
                json_data['message'] = na.body
                json_data['action_link'] = na.action_link
                na.push_data=json.dumps(json_data)
                naa = NotificationAttributeAdapter(user=user,type=NotificationTypes.PUSH,attribute=na)
                push_attributes.append(naa)
    
    return {
        NotificationTypes.IN_APP:in_app_attributes,
        NotificationTypes.EMAIL:email_attributes,
        NotificationTypes.PUSH:push_attributes
    }

def create_notification_type_attributes_email(user_emails,obj,na):
    email_attributes = []
    for user_email in user_emails:
        na.email_template = format_message(na.email_template,{'obj':obj,'user_email':user_email,'action_link':na.action_link})
        na.email_attachment_url=na.image_url
        naa = NotificationAttributeAdapter(user_email=user_email,type=NotificationTypes.EMAIL,attribute=na)
        email_attributes.append(naa)

    return {
        NotificationTypes.EMAIL:email_attributes
    }

    