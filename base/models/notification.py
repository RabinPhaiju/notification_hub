import uuid
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .subject_choices import NotificationSubject,DefaultNotificationSubject

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Notification(BaseModel):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=20,choices=NotificationSubject.choices)
    slug = models.SlugField(max_length=100, unique=False, null=True, blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class UserNotificationSettings(BaseModel):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='notification_settings')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, choices=NotificationSubject.choices, 
        default=DefaultNotificationSubject.ALL, null=True, blank=True)

    unique_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    notifications_enabled = models.BooleanField(default=True)

    in_app = models.BooleanField(default=True)
    email = models.BooleanField(default=True)
    push_notification = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'content_type', 'subject')

    def save(self, *args, **kwargs):
    # Generate UUID based on user_id, content_type, and subject
        if not self.unique_key:
            self.unique_key = uuid.uuid5(
                uuid.NAMESPACE_DNS, 
                f"{self.user_id}-{self.content_type_id}-{self.subject}"
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s {self.subject} settings for {self.content_type.model}"
    

class NotificationSubscriber(models.Model):
    subscribers = models.ManyToManyField('auth.User', related_name='notification_subscribers')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,related_name='subscriber_model')
    generic_object_id = models.PositiveIntegerField(null=True, blank=True)
    generic_object = GenericForeignKey('content_type', 'generic_object_id')

    def __str__(self):
        return f"{self.content_type.model} {self.generic_object_id}"
