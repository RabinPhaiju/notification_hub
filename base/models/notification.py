from dataclasses import dataclass
from typing import Optional
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .subject_choices import NotificationSubjectChoices

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
    category = models.CharField(max_length=20,choices=NotificationSubjectChoices.choices) # rename to subject
    action_link = models.URLField(blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=False, null=True, blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class UserNotificationSetting(BaseModel):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='notification_settings')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, choices=NotificationSubjectChoices.choices, null=True, blank=True)

    notifications_enabled = models.BooleanField(default=True)

    in_app = models.BooleanField(default=True)
    email = models.BooleanField(default=True)
    push = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'content_type', 'subject')

    def __str__(self):
        return f"{self.user.username}--{self.content_type.model}--{self.subject}"
    
class NotificationSubscriber(models.Model):
    subscribers = models.ManyToManyField('auth.User', related_name='notification_subscribers')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,related_name='subscriber_model')
    generic_object_id = models.PositiveIntegerField(null=True, blank=True)
    generic_object = GenericForeignKey('content_type', 'generic_object_id')

    def __str__(self):
        return f"{self.content_type.model} {self.generic_object_id}"

@dataclass
class NotificationAttribute:
    title: Optional[str] = None
    body: Optional[str] = None
    action_link: Optional[str] = None
    image_url: Optional[str] = None
    email_template: Optional[str] = None
    email_attachment_url: Optional[str] = None
    push_data: Optional[str] = None

    def as_dict(self, type):
        if type == 'email':
            return {
                'title': self.title,
                'body': self.body,
                'email_template': self.email_template,
                'email_attachment_url': self.email_attachment_url,
            }
        elif type == 'push':
            return {
                'title': self.title,
                'body': self.body,
                'push_data': self.push_data,
            }
        elif type == 'in_app':
            return {
                'title': self.title,
                'body': self.body,
                'action_link': self.action_link,
                'image_url': self.image_url,
            }
        return {}
    
@dataclass
class NotificationAttributeAdapter:
    attribute: object = None
    user: object = None
    type: object = None

    def __str__(self):
        return f"NotificationAttribute for {self.user} via {self.notification_type}"