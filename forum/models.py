from django.db import models
from base.mixins import NotificationModelMixin

class ForumPost(NotificationModelMixin,models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE,null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
