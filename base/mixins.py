from django.contrib.contenttypes.models import ContentType
from base.models import UserNotificationSettings,Notification
from django.db.models import Q
from django.core import mail
from base.models import DefaultNotificationSubject
from django.conf import settings
from django.db.models import Count

class NotificationMixin:
    def notify_subscribers(self, subject,type, **kwargs):
        if(type == 'email'):
            email_from = 'app@collection.ai'
            email_subject = kwargs.get('emailSubject')
            email_body = kwargs.get('emailBody')
            content_type = ContentType.objects.get_for_model(self.__class__)

            subscribers_to_notify = UserNotificationSettings.objects.filter(
                Q(user__notification_subscribers__content_type=content_type),
                Q(user__notification_subscribers__generic_object_id=self.id),
                Q(subject__in=[subject,DefaultNotificationSubject.ALL]),
                Q(notifications_enabled = True) ,
                Q(email=True)
            ).select_related('user')

            user_emails = subscribers_to_notify.values_list('user__email', flat=True)
            for user_email in user_emails:
                # mail.send_mail(
                #     email_subject,
                #     email_body,
                #     email_from,
                #     [user_email],
                #     fail_silently=False,
                # )


                # message = mail.EmailMessage(
                #     email_subject,
                #     email_body,
                #     email_from,
                #     [user_email],
                # )
                # file_path = os.path.join(settings.BASE_DIR, "test_image.png")
                # message.attach_file(file_path)
                # message.send()

                html_content = "<p>This is an <strong>important</strong> message.</p>"
                msg = mail.EmailMultiAlternatives(email_subject, email_body, email_from, [user_email])
                msg.attach_alternative(html_content, "text/html")
                # msg.content_subtype = "html"
                msg.send()
        elif (type == 'in_app'):
            title = kwargs.get('title')
            description = kwargs.get('description')
            content_type = ContentType.objects.get_for_model(self.__class__)

            subscribers_with_in_app_notify = UserNotificationSettings.objects.filter(
                Q(user__notification_subscribers__content_type=content_type),
                Q(user__notification_subscribers__generic_object_id=self.id),
                Q(subject__in=[subject,DefaultNotificationSubject.ALL]),
                Q(notifications_enabled = True) ,
                Q(in_app=True)
            ).select_related('user')

            for notification_setting in subscribers_with_in_app_notify:
                user = notification_setting.user
                Notification.objects.create( #  bulk_create does not trigger model signals (e.g., post_save or pre_save).
                    user=user,
                    title=title,
                    description=description,
                    category=subject
                )
        elif type == 'push_notification':
            content_type = ContentType.objects.get_for_model(self.__class__)
            subscribers_with_push_notify = UserNotificationSettings.objects.filter(
                Q(user__notification_subscribers__content_type=content_type),
                Q(user__notification_subscribers__generic_object_id=self.id),
                Q(subject__in=[subject,DefaultNotificationSubject.ALL]),
                Q(notifications_enabled = True) ,
                Q(push_notification=True)
            ).select_related('user')
            # .select_related('user').distinct('user') # postgres only

            for user in set(list(e.user for e in subscribers_with_push_notify)):
                print(user.email)
        else:
            print('Notification type not supported')