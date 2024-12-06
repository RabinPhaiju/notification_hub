from base.models import Notification
from django.core import mail
from base.utils import Utils

class NotificationModelMixin:
    def notify_subscribers(self, subject, types, **kwargs):
        default_types = ['notifications_enabled']
        types = list(set(default_types+types))
        title = kwargs.get('title')
        description = kwargs.get('description')
        user_group = Utils.get_user_group_settings(self.__class__,self.id, subject, types)

        for user in user_group:
            if user_group[user]['all']['notifications_enabled'] and user_group[user][subject]['notifications_enabled']:
                if 'in_app' in types and user_group[user]['all']['in_app'] and user_group[user][subject]['in_app']:
                    Notification.objects.create(
                        user=user,
                        title=title,
                        description=description,
                        category=subject
                    )
                if 'email' in types and user_group[user]['all']['email'] and user_group[user][subject]['email']:
                        email_from = 'app@collection.ai'
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
                        msg = mail.EmailMultiAlternatives(title, description, email_from, [user.email])
                        msg.attach_alternative(html_content, "text/html")
                        # msg.content_subtype = "html"
                        msg.send()
                           
                if 'push_notification' in types and user_group[user]['all']['push_notification'] and user_group[user][subject]['push_notification']: 
                    print('push_notification',user,user_group[user])
