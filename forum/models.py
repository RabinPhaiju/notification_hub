from django.db import models
from base.mixins import NotificationModelMixin

class ForumPost(NotificationModelMixin,models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE,null=True)

    @property
    def action_link(self):
        return f"/forum/{self.id}"

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class ForumPostReply(NotificationModelMixin,models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='replies')
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True)

    @property
    def action_link(self):
        return f"/forum/{self.post.id}"
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Reply to {self.post.title} by {self.created_by.username}"
