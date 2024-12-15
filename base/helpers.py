from .models import MailMessage,CloudMessage,NotificationAttributeAdapter,Notification
from .utils import get_model_attributes,format_message
from django.conf import settings

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

def sent_email_notification(attributes, emails=None, is_bulk=True):
    if emails and not isinstance(emails, list):
        raise ValueError("Emails must be a list of email addresses.")
    
    if emails: # Create notifications for multiple emails with shared attributes
        if not isinstance(attributes, NotificationAttributeAdapter):
            raise ValueError("For email list, notification_attributes must be a single dict.")
        
        mail_notifications = [
            MailMessage(
                subject=attributes.title,
                body=attributes.email_template if attributes.email_template !='' else attributes.body,
                attachment_url=attributes.email_attachment_url,
                sender_email=settings.DEFAULT_FROM_EMAIL, 
                recipient_emails=email
                )
            for email in emails
        ]
        MailMessage.objects.bulk_create(mail_notifications)

    elif is_bulk: # Handle bulk creation with list of attributes
        if not isinstance(attributes, list):
            raise ValueError("For bulk creation, notification_attributes must be a list of dicts.")
        
        mail_notifications = [
            MailMessage(
                subject=naa.attribute.title,
                body=naa.attribute.email_template if naa.attribute.email_template !='' else naa.attribute.body,
                attachment_url=naa.attribute.email_attachment_url or naa.attribute.image_url,
                sender_email=settings.DEFAULT_FROM_EMAIL,
                recipient_emails=','.join([naa.user_email]),
            ) 
            for naa in attributes
        ]
        MailMessage.objects.bulk_create(mail_notifications)

    else: # Handle individual email case
        if not isinstance(attributes, dict):
            raise ValueError("For single email, notification_attributes must be a dict.")
        
        MailMessage.objects.create(
            subject=attributes['subject'],
            body=attributes['body'],
            attachment_url=attributes['attachment_url'],
            sender_email=settings.DEFAULT_FROM_EMAIL,
            recipient_emails=','.join(attributes['email']),
        )
