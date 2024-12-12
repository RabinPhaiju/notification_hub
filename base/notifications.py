from base.models import NotificationSubjectAll,MailMessage,CloudMessage,NotificationAttributeAdapter,Notification
import json
from utils import get_model_attributes,format_message
from django.core.mail import EmailMessage
from base.enums import NotificationTypes

def create_notification_attributes_from_users(obj,user_group,subject,types,notification_attribute):
    notification_type_attributes = {
        NotificationTypes.IN_APP:[],
        NotificationTypes.EMAIL:[],
        NotificationTypes.PUSH_NOTIFICATION:[]
    }

    na = notification_attribute or get_model_attributes(obj,subject)
    na.action_link = na.action_link or getattr(obj, 'action_link', '') if hasattr(obj, 'action_link') else ''
    na.image_url=na.image_url or getattr(obj, 'image_url', '') if hasattr(obj, 'image_url') else ''

    for user in user_group:
        # check if user have 'subject' settings
        if not user_group[user].get(subject,False):
            user_group[user][subject.lower()] = {
                NotificationTypes.NOTIFICATIONS_ENABLED:True,
                NotificationTypes.IN_APP:True,
                NotificationTypes.EMAIL:True,
                NotificationTypes.PUSH_NOTIFICATION:True
                }

        if user_group[user][NotificationSubjectAll.ALL][NotificationTypes.NOTIFICATIONS_ENABLED] and user_group[user][subject][NotificationTypes.NOTIFICATIONS_ENABLED]:
            if NotificationTypes.IN_APP in types and\
            user_group[user][NotificationSubjectAll.ALL][NotificationTypes.IN_APP] and\
            user_group[user][subject][NotificationTypes.IN_APP]:
                naa = NotificationAttributeAdapter(user=user,type=NotificationTypes.IN_APP,attribute=na)
                notification_type_attributes[NotificationTypes.IN_APP].append(naa)

            if NotificationTypes.EMAIL in types and\
            user_group[user][NotificationSubjectAll.ALL][NotificationTypes.EMAIL] and\
            user_group[user][subject][NotificationTypes.EMAIL]:
                na.email_html = format_message(na.email_html,{'obj':obj,'user':user,'action_link':na.action_link})
                na.email_attachment_url=na.image_url
                naa = NotificationAttributeAdapter(user=user,type=NotificationTypes.EMAIL,attribute=na)
                notification_type_attributes[NotificationTypes.EMAIL].append(naa)

            if NotificationTypes.PUSH_NOTIFICATION in types and\
            user_group[user][NotificationSubjectAll.ALL][NotificationTypes.PUSH_NOTIFICATION] and\
            user_group[user][subject][NotificationTypes.PUSH_NOTIFICATION]: 
                json_data = json.loads(na.push_data or '{}')
                json_data['id'] = str(obj.id)
                json_data['message'] = na.body
                json_data['action_link'] = na.action_link
                na.push_data=json.dumps(json_data)
                naa = NotificationAttributeAdapter(user=user,type=NotificationTypes.PUSH_NOTIFICATION,attribute=na)
                notification_type_attributes[NotificationTypes.PUSH_NOTIFICATION].append(naa)
    
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
        for una in notification_type_attributes[NotificationTypes.IN_APP]
    ]
    Notification.objects.bulk_create(settings_to_create_in_app)
    
    settings_to_create_mail = [
        MailMessage(
            subject=una.attribute.title,
            body=una.attribute.email_html if una.attribute.email_html !='' else una.attribute.body,
            attachment_url=una.attribute.email_attachment_url,
            sender_email='app@example.com',
            recipient_emails=','.join([una.user.email]),
        )
        for una in notification_type_attributes[NotificationTypes.EMAIL]
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
        for una in notification_type_attributes[NotificationTypes.PUSH_NOTIFICATION]
    ]
    CloudMessage.objects.bulk_create(settings_to_create_cloud)
