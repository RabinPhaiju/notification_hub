from base.models import UserNotificationSetting,NotificationSubjectAll,NotificationAttribute,MailMessage,CloudMessage,NotificationAttributeAdapter,Notification
import json
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

def get_user_group_settings(model,object_id, subject, types):
    user_group = dict()
    content_type = ContentType.objects.get_for_model(model)
    subscribers_settings_subject = UserNotificationSetting.objects.filter(
        Q(user__notification_subscribers__content_type=content_type),
        Q(user__notification_subscribers__generic_object_id=object_id),
        Q(content_type=content_type),
        Q(subject__in=[subject,NotificationSubjectAll.ALL]),
    ).select_related('user')

    for subscriber_setting in subscribers_settings_subject:
        if subscriber_setting.user not in user_group:
            user_group[subscriber_setting.user] = {
                    subscriber_setting.subject: {
                        **{type_key: getattr(subscriber_setting, type_key) for type_key in types},
                    }
                }
        user_group[subscriber_setting.user][subscriber_setting.subject] = {
                    **{type_key: getattr(subscriber_setting, type_key) for type_key in types},
        }
    return user_group

def get_user_model_settings(model,subject,types):
    user_group = dict()
    content_type = ContentType.objects.get_for_model(model)
    subscribers_settings_subject = UserNotificationSetting.objects.filter(
        Q(content_type=content_type),
        Q(subject__in=[subject,NotificationSubjectAll.ALL]),
    ).select_related('user')

    for subscriber_setting in subscribers_settings_subject:
        if subscriber_setting.user not in user_group:
            user_group[subscriber_setting.user] = {
                    subscriber_setting.subject: {
                        **{type_key: getattr(subscriber_setting, type_key) for type_key in types},
                    }
                }
        user_group[subscriber_setting.user][subscriber_setting.subject] = {
                    **{type_key: getattr(subscriber_setting, type_key) for type_key in types},
        }
    return user_group

def get_user_not_in_group_all(model):
    content_type = ContentType.objects.get_for_model(model)
    return User.objects.filter(
            ~Q(notification_settings__content_type=content_type),
        )

def get_model_attributes(model,subject,type):
        return {
            'ForumPost':{
                'new_post': {
                    'in_app': {
                        'title': 'Your post has been published!',
                        'body': 'Your new post is now live on the forum. Check it out.',
                        'action_link': 'forum/',
                    },
                    'email': {
                        'title': 'Your post is live on the forum!',
                        'body': 'We’re excited to let you know that your new post has been successfully published.',
                        'email_html': '<h1>Your post is live!</h1><p>Check it out on the forum now.</p>',
                        
                    },
                    'push_notification': {
                        'title': 'New Post Published',
                        'body': 'Your latest forum post is now live. Tap to view!',
                        'push_data': '{"action": "view_post", "message": "Your latest post is live!"}',
                    },
                },
            },
            'ForumPostReply':{
                'new_reply': {
                    'in_app': {
                        'title': 'A reply to your post has been published!',
                        'body': '',
                        'action_link': 'forum/reply/',
                    },
                    'email': {
                        'title': 'Your reply is live on the forum!',
                        'body': 'We’re excited to let you know that your new reply has been successfully published.',
                        'email_html': '<h1>Your reply is live!</h1><p>Check it out on the forum now.</p>',
                    },
                    'push_notification': {
                        'title': 'New Reply Published',
                        'body': 'A new reply to your latest forum post is now live. Tap to view!',
                        'push_data': '{"action": "view_post", "message": "Your latest reply is live!"}',
                    },
                },
            },
            'Offer':{
                'new_offer': {
                    'in_app': {
                        'title': 'Your offer has been published!',
                        'body': 'Your new offer is now live on the marketplace. Check it out.',
                        'action_link': 'marketplace/',
                    },
                    'email': {
                        'title': 'Your offer is live on the marketplace!',
                        'body': 'We’re excited to let you know that your new offer has been successfully published.',
                        'email_html': '<h1>Your offer is live!</h1><p>Check it out on the marketplace now.</p>',
                    },
                    'push_notification': {
                        'title': 'New Offer Published',
                        'body': 'Your latest offer is now live. Tap to view!',
                        'push_data': '{"action": "view_post", "message": "Your latest offer is live!"}',
                    }
                }
            }
        }[model][subject][type]

def create_notification_attributes_from_users(obj,user_group,subject,types,notification_attribute):
    notification_attributes = {
        'in_app':[],
        'email':[],
        'push_notification':[]
    }
    for user in user_group:
        # check if user have 'subject' settings
        if not user_group[user].get(subject,False):
            user_group[user][subject.lower()] = {'notifications_enabled':True,'in_app':True,'email':True,'push_notification':True}

        if user_group[user][NotificationSubjectAll.ALL]['notifications_enabled'] and user_group[user][subject]['notifications_enabled']:
            if 'in_app' in types and\
            user_group[user][NotificationSubjectAll.ALL]['in_app'] and\
            user_group[user][subject]['in_app']:
                model_attributes = get_model_attributes(obj.__class__.__name__,subject,'in_app')
                na = NotificationAttribute(
                        title=model_attributes['title'], body=model_attributes['body'],
                        action_link=model_attributes['action_link']+str(obj.id),
                        image_url=getattr(obj, 'image_url', '') if hasattr(obj, 'image_url') else '',
                        )
                naa = NotificationAttributeAdapter(
                    user=user,
                    notification_type='in_app',
                    notification_attribute=notification_attribute or na
                    )
                notification_attributes['in_app'].append(naa)
                # Create notification_attribute from another method, that gathers all attributes from respective model or hardcoded.

            if 'email' in types and\
            user_group[user][NotificationSubjectAll.ALL]['email'] and\
            user_group[user][subject]['email']:
                model_attributes = get_model_attributes(obj.__class__.__name__,subject,'email')
                na = NotificationAttribute(
                    title=model_attributes['title'], body=model_attributes['body'],
                    email_html=model_attributes['email_html'],
                    email_attachment=getattr(obj, 'image_url', '') if hasattr(obj, 'image_url') else '',
                    )
                naa = NotificationAttributeAdapter(
                    user=user,
                    notification_type='email',
                    notification_attribute=notification_attribute or na)
                notification_attributes['email'].append(naa)

            if 'push_notification' in types and\
            user_group[user][NotificationSubjectAll.ALL]['push_notification'] and\
            user_group[user][subject]['push_notification']: 
                model_attributes = get_model_attributes(obj.__class__.__name__,subject,'push_notification')
                json_data = json.loads(model_attributes['push_data'])
                json_data['id'] = str(obj.id)
                na = NotificationAttribute(
                    title=model_attributes['title'], body=model_attributes['body'],
                    push_data=json.dumps(json_data),
                    )
                naa = NotificationAttributeAdapter(
                    user=user,
                    notification_type='push_notification',
                    notification_attribute=notification_attribute or na)
                notification_attributes['push_notification'].append(naa)
    
    # Sent Notification
    settings_to_create_in_app = [
        Notification(
            user=una.user,
            title=una.notification_attribute.title,
            description=una.notification_attribute.body,
            category=subject,
            action_link=una.notification_attribute.action_link,
            image_url=una.notification_attribute.image_url
            )
        for una in notification_attributes['in_app']
    ]
    Notification.objects.bulk_create(settings_to_create_in_app)
    
    settings_to_create_mail = [
        MailMessage(
            subject=una.notification_attribute.title,
            body=una.notification_attribute.email_html if una.notification_attribute.email_html !='' else una.notification_attribute.body,
            attachment=una.notification_attribute.email_attachment,
            sender_email='app@example.com',
            recipient_emails=','.join([una.user.email]),
        )
        for una in notification_attributes['email']
    ]
    MailMessage.objects.bulk_create(settings_to_create_mail)

    settings_to_create_cloud = [
        CloudMessage(
            user=una.user,
            title=una.notification_attribute.title,
            body=una.notification_attribute.body,
            data=una.notification_attribute.push_data
        )
        for una in notification_attributes['push_notification']
    ]
    CloudMessage.objects.bulk_create(settings_to_create_cloud)
