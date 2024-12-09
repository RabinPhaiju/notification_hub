from django.db import models
from base.mixins import NotificationModelMixin

class Offer(NotificationModelMixin,models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    email_template = models.TextField(blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title
