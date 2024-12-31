from .models import MailMessage,CloudMessage,NotificationAttributeAdapter,Notification,NotificationSubjectAll,PriorityChoices
import json
from typing import Optional,Dict
from copy import deepcopy
from .utils import get_model_attributes,format_message
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth.models import AnonymousUser
from .enums import NotificationTypes
from push_notifications.models import GCMDevice
from push_notifications.gcm import send_message, dict_to_fcm_message

def format_notification_attribute(obj,subject,notification_attribute):
    na = notification_attribute or get_model_attributes(obj,subject)
    na.title = format_message(na.title,{'obj':obj})
    na.body = format_message(na.body,{'obj':obj})
    na.action_link = na.action_link or getattr(obj, 'action_link', '') if hasattr(obj, 'action_link') else ''
    na.image_url=na.image_url or getattr(obj, 'image_url', '') if hasattr(obj, 'image_url') else ''
    na.image_url = format_message(na.image_url,{'obj':obj})
    return na

def get_notification_type_attributes_users(target_user_group,subject,types,obj,na):
    in_app_attributes = []
    email_attributes = []
    push_attributes = []
    for user in target_user_group:
        # check if user have 'subject' settings
        if not target_user_group[user].get(subject,False):
            target_user_group[user][subject.lower()] = {
                NotificationTypes.NOTIFICATIONS_ENABLED:True, NotificationTypes.IN_APP:True,
                NotificationTypes.EMAIL:True, NotificationTypes.PUSH:True
                }

        # check if user have 'all' and 'subject' settings enabled
        if target_user_group[user][NotificationSubjectAll.ALL][NotificationTypes.NOTIFICATIONS_ENABLED] and target_user_group[user][subject][NotificationTypes.NOTIFICATIONS_ENABLED]:
            if NotificationTypes.IN_APP in types and\
            target_user_group[user][NotificationSubjectAll.ALL][NotificationTypes.IN_APP] and target_user_group[user][subject][NotificationTypes.IN_APP]:
                # to support push in in_app
                in_app_attributes.append(get_push_notification_attributes(obj,user,na,NotificationTypes.IN_APP))

            if NotificationTypes.EMAIL in types and\
            target_user_group[user][NotificationSubjectAll.ALL][NotificationTypes.EMAIL] and target_user_group[user][subject][NotificationTypes.EMAIL]:
                email_attributes.append(get_email_notification_attributes(obj,user,na))

            if NotificationTypes.PUSH in types and\
            target_user_group[user][NotificationSubjectAll.ALL][NotificationTypes.PUSH] and target_user_group[user][subject][NotificationTypes.PUSH]: 
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

def get_email_notification_attributes(obj,user,_na):
    na = deepcopy(_na)
    na.email_template = format_message(na.email_template,{'obj':obj,'user':user,'action_link':na.action_link})
    na.email_attachment_id=na.email_attachment_id or getattr(obj, 'email_attachment_id', '')
    return NotificationAttributeAdapter(user=user,type=NotificationTypes.EMAIL,attribute=na)

def get_push_notification_attributes(obj,user,_na,type=NotificationTypes.PUSH):
    na = deepcopy(_na)
    json_data = json.loads(na.push_data or '{}') # can be moved to format_notification_attribute
    json_data['id'] = str(obj.id)
    json_data['title'] = na.title
    json_data['message'] = na.body
    json_data['action_link'] = na.action_link
    # json_data['image_url'] = na.image_url
    # format message
    for key,value in json_data.items():
        json_data[key] = format_message(value,{'obj':obj})

    na.push_data=json.dumps(json_data)
    return NotificationAttributeAdapter(user=user,type=type,attribute=na)

def sent_in_app(in_app_messages):
    if isinstance(in_app_messages, Notification):
        in_app_messages = [in_app_messages]
    elif not isinstance(in_app_messages,list):
        raise ValueError("in_app_messages must be a list or a single Notification instance.")
    elif len(in_app_messages) == 0:
        return
    
    # better to create Notification class instance here not passing or warp with other object
    Notification.objects.bulk_create(in_app_messages)

def build_push_message(
    title: Optional[str] = None,
    body: Optional[str] = None,
    message: Optional[str] = None,
    data: Optional[Dict] = None,
    time_to_live: Optional[int] = None,
    priority: Optional[str] = None,
    condition: Optional[str] = None,
    topic: Optional[str] = None,
    android_config: Optional[Dict] = None,  # For Android-specific settings
    ios_config: Optional[Dict] = None,      # For iOS-specific settings
    platform: Optional[str] = None,
    channel_id: Optional[str] = None
) -> Dict:
    # Generic settings
    message_kwargs = {
        'icon': 'myicon',
        'sound': 'default',
        'badge': 1,
        'click_action': 'OPEN_ACTIVITY',
        'priority': 'high',
        'time_to_live': 3600,
        'collapse_key': 'my_collapse_key', # preventing message flooding.

        # Used for localization
        # 'title_loc_key': None,
        # 'title_loc_args': None,
        # 'body_loc_key': None,
        # 'body_loc_args': None,
    }

    if message:
        message_kwargs['message'] = message
    if title:
        message_kwargs['title'] = title
    if body:
        message_kwargs['body'] = body
    if data:
        message_kwargs['data'] = data
    if time_to_live:
        message_kwargs['time_to_live'] = time_to_live
    if priority:
        message_kwargs['priority'] = priority
    if condition:
        message_kwargs['condition'] = condition
    if topic:
        message_kwargs['topic'] = topic

    if android_config and (platform is None or platform.lower() == "android"):
        message_kwargs['android'] = {"notification": android_config}
        message_kwargs['android']['notification']['channel_id'] = channel_id
        if data:
            message_kwargs['data']["platform"] = "android"
    if ios_config and (platform is None or platform.lower() == "ios"):
        message_kwargs['apns'] = {"payload": {"aps": ios_config}}
        if data:
            message_kwargs['data']["platform"] = "ios"

    if platform is not None and platform.lower() not in ["android", "ios"]:
        raise ValueError("Invalid platform specified. Must be 'android' or 'ios'.")

    return message_kwargs

def sent_mail(email_messages):
    if isinstance(email_messages, EmailMessage):
        email_messages = [email_messages]
    elif not isinstance(email_messages, list):
        raise ValueError("email_messages must be a list or a single EmailMessage instance.")
    elif len(email_messages) == 0:
        return
    
    # Send the emails
    # for email_message in email_messages:
        # email_message.send()

    mail_messages = [
        MailMessage(
            subject=email_message.subject,
            body=email_message.body,
            attachment_url='',
            sender_email=settings.DEFAULT_FROM_EMAIL,
            recipient_emails=','.join(email_message.recipients())
        ) 
        for email_message in email_messages
    ]
    MailMessage.objects.bulk_create(mail_messages)
    
def sent_push(push_messages): # for now its list of dict
    if not isinstance(push_messages, list):
        raise ValueError("push_messages must be a list.")
    elif len(push_messages) == 0:
        return

    push_messages_to_create = [
        CloudMessage(
            user=push_message['user'],
            title=push_message['title'],
            body=push_message['body'],
            data=push_message['data'],
            priority=push_message.get('priority', PriorityChoices.NORMAL.value),
        ) 
        for push_message in push_messages
    ]

    CloudMessage.objects.bulk_create(push_messages_to_create)

    # sent push notification
    # devices = GCMDevice.objects.get(user=user)
    # sent_push_notification(devices, title=title, body=body, data=data)

def sent_push_notification(devices, **kwargs) -> None:
    try:
        message_kwargs = build_push_message(**kwargs)
        print(message_kwargs)
        # result,response = devices.send_message(message=None,data=None,**message_kwargs)
        print(f"Message sent successfully {'result'}")
    except Exception as e:
        print(f"Error sending message: {e}")

def sent_topic_notification(**kwargs) -> None:
    try:
        message_kwargs = build_push_message(**kwargs)
        print("Message Payload:", message_kwargs)
        fcm_message = dict_to_fcm_message(message_kwargs)

        topic = kwargs.get('topic')
        condition = kwargs.get('condition')

        if topic:
            send_message(None, fcm_message, to=f"/topics/{topic}")
            print(f"Message sent successfully to topic '{topic}'.")
        elif condition:
            send_message(None, fcm_message, to=condition)
            print(f"Message sent successfully to condition '{condition}'.")
        else:
            raise ValueError("Either 'topic' or 'condition' must be provided.")
    except Exception as e:
        print(f"Error sending message: {e}")