from django.contrib import admin

# Register your models here.
from .models import Notification, NotificationSubscriber, UserNotificationSettings

admin.site.register(Notification)
admin.site.register(NotificationSubscriber)
admin.site.register(UserNotificationSettings)