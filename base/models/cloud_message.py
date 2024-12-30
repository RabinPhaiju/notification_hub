from django.db import models
from .choices import PriorityChoices
class CloudMessage(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    # dont store that can be calculated. (devices)
    title = models.CharField(max_length=200)
    body = models.TextField()
    data = models.JSONField(blank=True, null=True, help_text="JSON data for payload.")
    priority = models.CharField(max_length=10, choices=PriorityChoices.choices, default=PriorityChoices.NORMAL)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
