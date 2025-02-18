from dataclasses import dataclass
from typing import Optional
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from ..registry import get_subject_choices
from .choices import PriorityChoices
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Notification(BaseModel):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    title = models.CharField(max_length=100)
    body = models.TextField(null=True, blank=True)
    data = models.JSONField(null=True, blank=True)  # Store custom data as JSON
    extra = models.JSONField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PriorityChoices.choices, default=PriorityChoices.NORMAL)
    image_url = models.URLField(blank=True, null=True)
    action_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class UserNotificationSetting(BaseModel):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='notification_settings')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, choices=get_subject_choices(), null=True, blank=True)

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
    email_attachment_id: Optional[str] = None
    push_data: Optional[str] = None

    # .copy() method

    def as_dict(self, type):
        if type == 'email':
            return {
                'title': self.title,
                'body': self.body,
                'email_template': self.email_template,
                'email_attachment_id': self.email_attachment_id,
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
    type: object = None # optional

    def __str__(self):
        return f"NotificationAttribute for {self.user} via {self.notification_type}"