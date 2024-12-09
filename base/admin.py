from django.contrib import admin

# Register your models here.
from .models import Notification, NotificationSubscriber, UserNotificationSetting,CloudMessage,MailMessage

admin.site.register(Notification)
admin.site.register(NotificationSubscriber)
admin.site.register(UserNotificationSetting)
admin.site.register(MailMessage)
admin.site.register(CloudMessage)