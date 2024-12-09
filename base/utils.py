from base.models import UserNotificationSetting,NotificationSubjectAll
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

class Utils:
    @staticmethod
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
            }
        }[model][subject][type]