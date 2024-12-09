from base.models import UserNotificationSetting
from django.contrib.contenttypes.models import ContentType
from utils import get_user_model_settings,get_user_group_settings,create_notification_attributes_from_users

class NotificationModelMixin:
    def notify_with_attribute(self, subject, types,attribute):
        pass

    def notify_all(self, subject, types):
        default_types = ['notifications_enabled']
        types = list(set(default_types+types))
        user_group = get_user_model_settings(self.__class__, subject, types)

        users_not_with_group = [u for u, details in user_group.items() if not details.get(subject)]
        if users_not_with_group:
            print(users_not_with_group)
            settings_to_create = [
                UserNotificationSetting(user=user, subject=subject, content_type=ContentType.objects.get_for_model(self.__class__))
                for user in users_not_with_group
            ]
            UserNotificationSetting.objects.bulk_create(settings_to_create)
        
        # Create Notifications
        create_notification_attributes_from_users(self,user_group,subject,types)
        

    def notify_subscribers(self, subject, types):
        default_types = ['notifications_enabled']
        types = list(set(default_types+types))
        user_group = get_user_group_settings(self.__class__,self.id, subject, types)

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
        create_notification_attributes_from_users(self,user_group,subject,types)
        
