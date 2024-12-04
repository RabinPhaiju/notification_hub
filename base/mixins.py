from django.contrib.contenttypes.models import ContentType
from base.models import UserNotificationSettings
from django.db.models import Q

class NotificationMixin:
    def notify(self, subject,type, **kwargs):
        if(type == 'email'):
            content_type = ContentType.objects.get_for_model(self.__class__)

            subscribers_with_in_app_notify = UserNotificationSettings.objects.filter(
                Q(user__notification_subscribers__content_type=content_type),
                Q(user__notification_subscribers__generic_object_id=self.id),
                Q(subject=subject),
                Q(notifications_enabled = True) ,
                Q(email=True)
            ).select_related('user')

            for notification_setting in subscribers_with_in_app_notify:
                user = notification_setting.user
                print(user.username)
        else:
            print('Notification type not supported')