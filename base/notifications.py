from base.models import NotificationSubjectAll,MailMessage,CloudMessage,NotificationAttributeAdapter,Notification
import json
from utils import get_model_attributes
from django.core.mail import EmailMessage

def create_notification_attributes_from_users(obj,user_group,subject,types,notification_attribute):
    notification_type_attributes = {
        'in_app':[],
        'email':[],
        'push_notification':[]
    }
    for user in user_group:
        # check if user have 'subject' settings
        if not user_group[user].get(subject,False):
            user_group[user][subject.lower()] = {'notifications_enabled':True,'in_app':True,'email':True,'push_notification':True}

        if user_group[user][NotificationSubjectAll.ALL]['notifications_enabled'] and user_group[user][subject]['notifications_enabled']:
            na = notification_attribute or get_model_attributes(obj,subject)
            na.action_link = getattr(obj, 'action_link', '') if hasattr(obj, 'action_link') else ''
            na.image_url=getattr(obj, 'image_url', '') if hasattr(obj, 'image_url') else ''

            if 'in_app' in types and\
            user_group[user][NotificationSubjectAll.ALL]['in_app'] and\
            user_group[user][subject]['in_app']:
                naa = NotificationAttributeAdapter(user=user,type='in_app',attribute=na)
                notification_type_attributes['in_app'].append(naa)

            if 'email' in types and\
            user_group[user][NotificationSubjectAll.ALL]['email'] and\
            user_group[user][subject]['email']:
                na.email_attachment=na.image_url
                naa = NotificationAttributeAdapter(user=user,type='email',attribute=na)
                notification_type_attributes['email'].append(naa)

            if 'push_notification' in types and\
            user_group[user][NotificationSubjectAll.ALL]['push_notification'] and\
            user_group[user][subject]['push_notification']: 
                json_data = json.loads(na.push_data)
                json_data['id'] = str(obj.id)
                json_data['message'] = na.body
                json_data['action_link'] = na.action_link
                na.push_data=json.dumps(json_data)
                naa = NotificationAttributeAdapter(user=user,type='push_notification',attribute=na)
                notification_type_attributes['push_notification'].append(naa)
    
    # Sent Notification
    settings_to_create_in_app = [
        Notification(
            user=una.user,
            title=una.attribute.title,
            description=una.attribute.body,
            category=subject,
            action_link=una.attribute.action_link,
            image_url=una.attribute.image_url
            )
        for una in notification_type_attributes['in_app']
    ]
    Notification.objects.bulk_create(settings_to_create_in_app)
    
    settings_to_create_mail = [
        MailMessage(
            subject=una.attribute.title,
            body=una.attribute.email_html if una.attribute.email_html !='' else una.attribute.body,
            # attachment=una.attribute.email_attachment,
            sender_email='app@example.com',
            recipient_emails=','.join([una.user.email]),
        )
        for una in notification_type_attributes['email']
    ]
    # for mail in settings_to_create_mail:
        # msg = EmailMessage(
        #     subject=mail.subject,
        #     body=mail.body,
        #     from_email=mail.sender_email,
        #     to=[mail.recipient_emails],
        # )
        # msg.content_subtype = "html"
        # msg.send()
    MailMessage.objects.bulk_create(settings_to_create_mail)

    settings_to_create_cloud = [
        CloudMessage(
            user=una.user,
            title=una.attribute.title,
            body=una.attribute.body,
            data=una.attribute.push_data
        )
        for una in notification_type_attributes['push_notification']
    ]
    CloudMessage.objects.bulk_create(settings_to_create_cloud)
