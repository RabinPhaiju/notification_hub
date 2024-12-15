from .models import MailMessage,CloudMessage,NotificationAttributeAdapter,Notification,NotificationSubjectAll
import json
from .utils import get_model_attributes,format_message
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from .enums import NotificationTypes

def format_notification_attribute(obj,subject,notification_attribute):
    na = notification_attribute or get_model_attributes(obj,subject)
    na.title = format_message(na.title,{'obj':obj})
    na.body = format_message(na.body,{'obj':obj})
    na.action_link = na.action_link or getattr(obj, 'action_link', '') if hasattr(obj, 'action_link') else ''
    na.image_url=na.image_url or getattr(obj, 'image_url', '') if hasattr(obj, 'image_url') else ''
    return na

def get_notification_type_attributes_users(user_group,subject,types,obj,na):
    in_app_attributes = []
    email_attributes = []
    push_attributes = []
    for user in user_group:
        # check if user have 'subject' settings
        if not user_group[user].get(subject,False):
            user_group[user][subject.lower()] = {
                NotificationTypes.NOTIFICATIONS_ENABLED:True, NotificationTypes.IN_APP:True,
                NotificationTypes.EMAIL:True, NotificationTypes.PUSH:True
                }

        if user_group[user][NotificationSubjectAll.ALL][NotificationTypes.NOTIFICATIONS_ENABLED] and user_group[user][subject][NotificationTypes.NOTIFICATIONS_ENABLED]:
            if NotificationTypes.IN_APP in types and\
            user_group[user][NotificationSubjectAll.ALL][NotificationTypes.IN_APP] and user_group[user][subject][NotificationTypes.IN_APP]:
                naa = NotificationAttributeAdapter(user=user,type=NotificationTypes.IN_APP,attribute=na)
                in_app_attributes.append(naa)

            if NotificationTypes.EMAIL in types and\
            user_group[user][NotificationSubjectAll.ALL][NotificationTypes.EMAIL] and user_group[user][subject][NotificationTypes.EMAIL]:
                email_attributes.append(get_email_notification_attributes(obj,user,na))

            if NotificationTypes.PUSH in types and\
            user_group[user][NotificationSubjectAll.ALL][NotificationTypes.PUSH] and user_group[user][subject][NotificationTypes.PUSH]: 
                push_attributes.append(get_push_notification_attributes(obj,user,na))
    
    return {
        NotificationTypes.IN_APP:in_app_attributes,
        NotificationTypes.EMAIL:email_attributes,
        NotificationTypes.PUSH:push_attributes
    }

def get_notification_type_attributes_email(user_emails,obj,na):
    email_attributes = []
    for user_email in user_emails:
        user = AnonymousUser()
        user.email = user_email
        email_attributes.append(get_email_notification_attributes(obj,user,na))

    return {
        NotificationTypes.EMAIL:email_attributes
    }

def get_email_notification_attributes(obj,user,na):
    na.email_template = format_message(na.email_template,{'obj':obj,'user':user,'action_link':na.action_link})
    na.email_attachment_url=na.email_attachment_url or getattr(obj, 'email_attachment_url', '')
    return NotificationAttributeAdapter(user=user,type=NotificationTypes.EMAIL,attribute=na)

def get_push_notification_attributes(obj,user,na):
    json_data = json.loads(na.push_data or '{}') # can be moved to format_notification_attribute
    json_data['id'] = str(obj.id)
    json_data['title'] = na.title
    json_data['message'] = na.body
    json_data['action_link'] = na.action_link
    na.push_data=json.dumps(json_data)
    return NotificationAttributeAdapter(user=user,type=NotificationTypes.PUSH,attribute=na)


def sent_push(attributes):
    if attributes:
        settings_to_create_cloud = [
            CloudMessage(
                user=una.user,
                title=una.attribute.title,
                body=una.attribute.body,
                data=una.attribute.push_data
            )
            for una in attributes
        ]
        CloudMessage.objects.bulk_create(settings_to_create_cloud)

def sent_in_app(notification_attributes):
    if notification_attributes:
        settings_to_create_in_app = [
            Notification(
                user=una.user,
                title=una.attribute.title,
                description=una.attribute.body,
                action_link=una.attribute.action_link,
                image_url=una.attribute.image_url
                )
            for una in notification_attributes
        ]
        Notification.objects.bulk_create(settings_to_create_in_app)

def sent_email(notification_attributes):
    mail_notifications = [
        MailMessage(
            subject=naa.attribute.title,
            body=naa.attribute.email_template if naa.attribute.email_template !='' else naa.attribute.body,
            attachment_url=naa.attribute.email_attachment_url,
            sender_email=settings.DEFAULT_FROM_EMAIL,
            recipient_emails=','.join([naa.user.email]),
        ) 
        for naa in notification_attributes
    ]
    MailMessage.objects.bulk_create(mail_notifications)

