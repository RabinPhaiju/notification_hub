from django.db import models
from base.mixins import NotificationModelMixin

class ForumPost(NotificationModelMixin,models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.title
