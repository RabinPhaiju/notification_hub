from .models import NotificationSubjectAll,MailMessage,CloudMessage,NotificationAttributeAdapter,Notification
import json
from .utils import get_model_attributes,format_message
from django.conf import settings
from .enums import NotificationTypes

def format_notification_attribute(obj,subject,notification_attribute):
    na = notification_attribute or get_model_attributes(obj,subject)
    na.title = format_message(na.title,{'obj':obj})
    na.body = format_message(na.body,{'obj':obj})
    na.action_link = na.action_link or getattr(obj, 'action_link', '') if hasattr(obj, 'action_link') else ''
    na.image_url=na.image_url or getattr(obj, 'image_url', '') if hasattr(obj, 'image_url') else ''

    return na

def sent_push_notification(attributes):
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

def sent_in_app_notification(attributes):
    if attributes:
        settings_to_create_in_app = [
            Notification(
                user=una.user,
                title=una.attribute.title,
                description=una.attribute.body,
                action_link=una.attribute.action_link,
                image_url=una.attribute.image_url
                )
            for una in attributes
        ]
        Notification.objects.bulk_create(settings_to_create_in_app)

def sent_email_notification(attributes):
    if attributes:
        settings_to_create_mail = [
            MailMessage(
                subject=una.attribute.title,
                body=una.attribute.email_template if una.attribute.email_template !='' else una.attribute.body,
                attachment_url=una.attribute.email_attachment_url,
                sender_email=settings.DEFAULT_FROM_EMAIL,
                recipient_emails=','.join([una.user_email]),
            )
            for una in attributes
        ]
        MailMessage.objects.bulk_create(settings_to_create_mail)

