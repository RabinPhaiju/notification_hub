from django.db import models
from base.mixins import NotificationModelMixin
from base.models import NotificationSubjectChoices

class Offer(NotificationModelMixin,models.Model):
    subject = models.CharField(max_length=20,choices=NotificationSubjectChoices.choices,null=True,blank=True)
    title = models.CharField(max_length=200)
    body = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()

    @property
    def action_link(self):
        return f'/offer/{self.id}'
    
    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title
