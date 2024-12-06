from base.models import UserNotificationSetting
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
            Q(subject__in=[subject,'all']),
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