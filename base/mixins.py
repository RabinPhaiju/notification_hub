from base.models import UserNotificationSetting,NotificationSubjectAll
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from .notifications import create_notification_attributes_from_users

class NotificationModelMixin:
    def notify(self, subject, types,**kwargs):
        default_types = ['notifications_enabled']
        types = list(set(default_types+types))
        only_subs = kwargs.get('only_subs',False)
        notification_attribute = kwargs.get('notification_attribute',None)
        content_type = ContentType.objects.get_for_model(self.__class__)
        user_group = dict()

        query = [
            Q(content_type=content_type),
            Q(subject__in=[subject,NotificationSubjectAll.ALL]),
        ]
        if only_subs:
            query.extend([
                Q(user__notification_subscribers__content_type=content_type),
                Q(user__notification_subscribers__generic_object_id=self.id),
            ])
        subscribers_settings = UserNotificationSetting.objects.filter(*query).select_related('user')

        for subscriber_setting in subscribers_settings:
            if subscriber_setting.user not in user_group:
                user_group[subscriber_setting.user] = {
                        subscriber_setting.subject: {
                            **{type_key: getattr(subscriber_setting, type_key) for type_key in types},
                        }
                    }
            user_group[subscriber_setting.user][subscriber_setting.subject] = {
                        **{type_key: getattr(subscriber_setting, type_key) for type_key in types},
            }

        # Bulk create user notification settings -- but bulk create dont work signals (post_save,pre_save,post_delete)
        users_not_with_group = [u for u, details in user_group.items() if not details.get(subject)]
        if users_not_with_group:
            settings_to_create = [
                UserNotificationSetting(user=user, subject=subject, content_type=ContentType.objects.get_for_model(self.__class__))
                for user in users_not_with_group
            ]
            instances = UserNotificationSetting.objects.bulk_create(settings_to_create)
            # Manually send the post_save signal
            # for instance in instances:
                # post_save.send(sender=UserNotificationSetting, instance=instance, created=True)

        # Create notifications
        create_notification_attributes_from_users(self,user_group,subject,types,notification_attribute)
        
