from base.models import Notification,UserNotificationSetting,NotificationSubjectAll,NotificationAttribute,MailMessage,CloudMessage
from django.db.models.signals import post_save
import json
from django.contrib.contenttypes.models import ContentType
from base.utils import Utils

class NotificationModelMixin:
    def notify_subscribers(self, subject, types):
        default_types = ['notifications_enabled']
        types = list(set(default_types+types))
        user_group = Utils.get_user_group_settings(self.__class__,self.id, subject, types)

        # Bulk create user notification settings -- but bulk create dont work signals (post_save,pre_save,post_delete)
        users_not_with_group = [u for u, details in user_group.items() if not details.get(subject)] 
        # TODO subject can be 'all' or 'subject'. what if 'all' is also not in user_group_settings
        settings_to_create = [
            UserNotificationSetting(user=user, subject=subject, content_type=ContentType.objects.get_for_model(self.__class__))
            for user in users_not_with_group
        ]
        instances = UserNotificationSetting.objects.bulk_create(settings_to_create)
        # Manually send the post_save signal
        # for instance in instances:
            # post_save.send(sender=UserNotificationSetting, instance=instance, created=True)

        # Create notifications
        for user in user_group:
            # check if user have 'subject' settings
            if not user_group[user].get(subject,False):
                user_group[user][subject.lower()] = {'notifications_enabled':True,'in_app':True,'email':True,'push_notification':True}

            if user_group[user][NotificationSubjectAll.ALL]['notifications_enabled'] and user_group[user][subject]['notifications_enabled']:
                if 'in_app' in types and\
                user_group[user][NotificationSubjectAll.ALL]['in_app'] and\
                user_group[user][subject]['in_app']:
                    model_attributes = Utils.get_model_attributes(self.__class__.__name__,subject,'in_app')
                    na = NotificationAttribute(
                         title=model_attributes['title'], body=model_attributes['body'],
                         action_link=model_attributes['action_link']+str(self.id),
                         image_url=getattr(self, 'image_url', '') if hasattr(self, 'image_url') else '',
                         )
                    # Bulk create notifications by storing Notification Attributes
                    Notification.objects.create(user=user,title=na.title,description=na.body,category=subject,action_link=na.action_link,image_url=na.image_url)

                if 'email' in types and\
                user_group[user][NotificationSubjectAll.ALL]['email'] and\
                user_group[user][subject]['email']:
                        email_from = 'app@collection.ai'
                        model_attributes = Utils.get_model_attributes(self.__class__.__name__,subject,'email')
                        na = NotificationAttribute(
                            title=model_attributes['title'], body=model_attributes['body'],
                            email_html=model_attributes['email_html'],
                            email_attachment=getattr(self, 'image_url', '') if hasattr(self, 'image_url') else '',
                            )
                        MailMessage.objects.create(
                             subject=na.title,
                             body=na.email_html if na.email_html !='' else na.body,
                             attachment=na.email_attachment,
                             sender_email=email_from,
                             recipient_emails=','.join([user.email]),
                        )

                if 'push_notification' in types and\
                user_group[user][NotificationSubjectAll.ALL]['push_notification'] and\
                user_group[user][subject]['push_notification']: 
                    model_attributes = Utils.get_model_attributes(self.__class__.__name__,subject,'push_notification')
                    json_data = json.loads(model_attributes['push_data'])
                    json_data['id'] = str(self.id)
                    na = NotificationAttribute(
                        title=model_attributes['title'], body=model_attributes['body'],
                        push_data=json.dumps(json_data),
                        )
                    CloudMessage.objects.create(
                            user=user,
                            title=na.title,
                            body=na.body,
                            data=na.push_data
                    )

        # Bulk create respective user notification settings
        # settings_to_create = [
        #     Notification(user=una.user,title=una.title,description=una.body,category=una.subject,action_link=una.action_link,image_url=una.image_url)
        #     for una in user_notification_attribute if una.type == 'in_app'
        # ]
        # Notification.objects.bulk_create(settings_to_create)
        
